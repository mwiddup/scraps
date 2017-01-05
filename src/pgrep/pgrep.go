// This program will look through a directory for all file
// *install.sh or *install_nn.sh and pull out their contents
// It will try and turn it in to absolute paths and find the
// files mentioned. If they're not there, messages are shown
// pgrep.go
// Copyright (C) 2016 vagrant <vagrant@vagrant-ubuntu-trusty-64>
//
// Distributed under terms of the MIT license.
//

package main

import (
	"bufio"
	"bytes"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func parse_args() (pat string, path string) { //checks for input, 2 values
	if len(os.Args) < 2 {
		log.Fatal("usage: pgrep <file_name> <pattern>")
	}
	path = os.Args[1]
	pat = os.Args[2]
	return
}

type patLine struct {
	file string
	line int
}

type Results struct {
	elapsed time.Duration
	patLine []patLine
}

//basic grep functionallity, returns a Results struct of each matched line
//includes matched line, line number in file, time taken to grab all lines
//no filtering or utilities performed
func grepFile(file string, pat []byte) Results {
	var patValue Results //create a new Results struct
	var myPat []patLine  //this is the 0 length slice of patLine structs
	start := time.Now()  //everyone loves timing things, grab a start time
	f, err := os.Open(file)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	i := 0
	for scanner.Scan() {
		i++ //this counter gives us the current line number being scanner'ed
		if bytes.Contains(scanner.Bytes(), pat) {
			myPat = append(myPat, patLine{file: scanner.Text(), line: i})
		} //found something, at the new struct to the slice of structs
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
	patValue.elapsed = time.Since(start) //total time taken set in the Results struct
	patValue.patLine = myPat             //set the slice of patLine structs in the Results struct
	return patValue
}

func main() { //where the magic happens, but does nothing except call stubs
	checkFiles()
}

func checkFiles() {
	pat, root := parse_args()
	begin := time.Now()
	allPass := true
	visit := func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), "install.sh") || strings.HasSuffix(f.Name(), "install_nn.sh")) { //does this file fit the filter (install*.sh)
			grepped := grepFile(path, []byte(pat)) //go and grep the contents of the file
			fault := false
			tme := grepped.elapsed
			fmt.Printf("=== RUN   %s\n", path)
			for i := range grepped.patLine {
				com := strings.Trim(grepped.patLine[i].file, " ") //clean up the string, remove whitespace
				lne := grepped.patLine[i].line
				n := strings.LastIndex(com, " ") + 1 //index of next item after string
				l := len(com)
				if _, err := os.Stat(root + com[n:l-1]); os.IsNotExist(err) { //does the file exist
					if !fault { //is there a problem in this file, fault print file name once
						fmt.Printf("--- FAIL: %s (%.2f seconds)\n", path, tme.Seconds())
						fault = true
						allPass = false //one fail means we all fail
					}
					fmt.Printf("\tFile:%03d: %s\n", lne, root+com[n:l-1]) //substringing
				}
			}
			if !fault {
				fmt.Printf("--- PASS: %s (%.2f seconds)\n", path, tme.Seconds())
			}
		}
		return nil
	}
	err := filepath.Walk(root, visit)
	if err != nil {
		fmt.Printf("Done broke")
	}
	end := time.Since(begin)
	if !allPass {
		fmt.Printf("FAIL\nexit status 1\nFAIL     Check Files\t%.3fs\n", end.Seconds())
	} else {
		fmt.Printf("PASS\nok\tCheck Files\t%.3fs\n", end.Seconds())
	}
}
