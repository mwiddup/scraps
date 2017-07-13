'''
Created on 16Jun.,2017

A place to chuck some big variables/settings stuff.

@author: mwiddup
'''
root_path = "C:\Users\mwiddup\workspace\Mass Updates of VC\code"

load_pat_match = ["(^.*)(^((?!75000).)*$)[\r\n]*(^ *)(DECLARE CONST_ERR_LOADFAILED)(\s*)(.*\n*.*;)",
                  "(^.*)(^((?!n_locate_s).)*$)[\r\n]*(^\s*)(DECLARE n_sqlcode\s{,12})(\s*)(.*;)",
                  "OF CURSOR '",
                  "^.*IF[\s\(]*n_rows_deleted[\s\S]*CONST_ERR_LOADFAILED;\s*END IF;",
                  "^(\s*)(DECLARE stmt_prepared\s*STATEMENT;)(\s*)(-- Obtain)"]
load_pat_replace = ["\\1\\2\\n\\4DECLARE CONST_ERR_CONDITION \\6CONDITION FOR SQLSTATE '75000';\\r\\n\\4\\5\\6\\7",
                    "\\1\\2\\r\\n\\4DECLARE n_locate_s, n_locate_e\\6 SMALLINT        DEFAULT 1;\\r\\n\\4\\5\\6\\7",
                    "OF CURSOR MESSAGES ON SERVER '",
                    "    IF (n_rows_deleted > 0 or n_rows_rejected > 0 or n_rows_skipped > 0 or (n_rows_read <> n_rows_loaded)) THEN\r\n        -- substringing out the message code\r\n        SET n_locate_s = LOCATE('''', vc_msg_retrieval,1) + 1;\r\n        SET n_locate_e = LOCATE('''', vc_msg_retrieval,n_locate_s + 1);\r\n        SET CONST_ERR_LOADFAILED = CONST_ERR_LOADFAILED\r\n           || '. Check: '\r\n           || SUBSTRING(vc_msg_retrieval, n_locate_s, n_locate_e - n_locate_s,CODEUNITS32);\r\n\r\n        -- telling the world we broke\r\n        SIGNAL SQLSTATE CONST_SQLSTATE_ERROR\r\n        SET MESSAGE_TEXT = CONST_ERR_LOADFAILED;\r\n    ELSE\r\n        -- removes messages on server\r\n        PREPARE stmt_prepared FROM vc_msg_removal;\r\n        EXECUTE stmt_prepared;\r\n    END IF;",
                    "\\1\\2\\3-- Create continue and exit handlers\\r\\n\\1DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;\\r\\n\\r\\n\\1DECLARE EXIT HANDLER FOR CONST_ERR_CONDITION BEGIN\\r\\n\\1\\1RESIGNAL;\\r\\n\\1END;\\3\\4"]
load_pat_ignore = "(^((?!--).)*)sysproc\.db2load.*$"

grant_pat_head = '^--\s*(?:NAME|AUTHOR)[ \t]*DATE[ \t]*(?:RELEASE)*[ \t]*DESCRIPTION'
grant_pat_tail = '(^\-{7,}\r*\n[^\-])'
grant_pat_ignore = "pii_batch"

strip_grants = '^.*GRANT.+[\r\n]*[\;\@][\r\n]*'

comment_load = ('-- Matthew Widdup', '20170616', 'DJDEV-735', 'Added Load capture of warnings and failures')
comment_grant_strip_add = ('-- Matthew Widdup', '20170619', 'Security', 'Stripped old grants, added new ones')
comment_grant_strip = ('-- Matthew Widdup', '20170620', 'Security', 'Stripped old grants')
comment_grant_add = ('-- Matthew Widdup', '20170621', 'Security', 'Added new grant standards')

grant_block_proc_pat = [ "^(\s*SPECIFIC )\s*(\w+)\.(\w+)",
                         "(CREATE\s*OR\s*REPLACE\s*PROCEDURE)\s*(\w+)\.(\w+)" ]
grant_block_proc = """BEGIN

  DECLARE routine_schema   VARCHAR(128);
  DECLARE routine_name     VARCHAR(128);

  SET routine_schema = '#SCHEMA#';
  SET routine_name = '#OBJECT#';

  -- Grant required access to non-PII instance owners
  EXECUTE IMMEDIATE 'GRANT EXECUTE ON SPECIFIC PROCEDURE '||routine_schema||'.'||routine_name||' TO USER prddwi01';
  EXECUTE IMMEDIATE 'GRANT EXECUTE ON SPECIFIC PROCEDURE '||routine_schema||'.'||routine_name||' TO USER '||SYSPROC.AUTH_GET_INSTANCE_AUTHID();

  -- Grant required access to non-PII roles used at run-time
  EXECUTE IMMEDIATE 'GRANT EXECUTE ON SPECIFIC PROCEDURE '||routine_schema||'.'||routine_name||' TO ROLE db2_batch';

  -- Grant required access to non-PII roles used by support staff
  EXECUTE IMMEDIATE 'GRANT EXECUTE ON SPECIFIC PROCEDURE '||routine_schema||'.'||routine_name||' TO ROLE support';

  -- Grant required access to PII roles used at run-time
  EXECUTE IMMEDIATE 'GRANT EXECUTE ON SPECIFIC PROCEDURE '||routine_schema||'.'||routine_name||' TO ROLE pii_batch';

END@"""

grant_block_tab_pat = ["schema_name = '(\w*)'.*[\r\n]*.*table_name = '(\w*)'",
                       "(CREATE\s*OR\s*REPLACE\s*PROCEDURE)\s*(\w+)\.(\w+)"]

grant_block_tab = """    -- Grant required access to non-PII instance owners
    EXECUTE IMMEDIATE 'GRANT CONTROL ON TABLE '||schema_name||'.'||table_name||' TO USER prddwi01';
    EXECUTE IMMEDIATE 'GRANT CONTROL ON TABLE '||schema_name||'.'||table_name||' TO USER '||SYSPROC.AUTH_GET_INSTANCE_AUTHID();

    -- Grant required access to non-PII roles used at run-time
    EXECUTE IMMEDIATE 'GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE '||schema_name||'.'||table_name||' TO ROLE db2_batch';

    -- Grant required access to non-PII roles used by support staff
    EXECUTE IMMEDIATE 'GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE '||schema_name||'.'||table_name||' TO ROLE support';
    EXECUTE IMMEDIATE 'GRANT SELECT ON TABLE '||schema_name||'.'||table_name||' TO ROLE rds_readonly';

    -- Grant required access to PII roles used at run-time
    EXECUTE IMMEDIATE 'GRANT SELECT, UPDATE, INSERT, DELETE ON '||schema_name||'.'||table_name||' TO ROLE pii_batch';"""

tb_pat_match = ["^[\w]*(IF.*)[\s\S]*FN_AUTH_ALLOWED[\s\S]*(END IF;[\s\S]*\Z)"]
tb_pat_replace = ["\\1\\r\\n  THEN\\r\\n" + grant_block_tab + "\\r\\n  \\2"]