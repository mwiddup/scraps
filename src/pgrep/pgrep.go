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
)

func parse_args() (pat string, path string) {
	if len(os.Args) < 2 {
		log.Fatal("usage: pgrep <file_name> <pattern>")
	}
	path = os.Args[1]
	pat = os.Args[2]
	return
}

//basic grep functionallity, returns a slice of each matched line
//no filtering or utilities performed
func grepFile(file string, pat []byte) []string {
	var patValue []string //don't know how efficient 0 len slice is
	f, err := os.Open(file)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		if bytes.Contains(scanner.Bytes(), pat) {
			patValue = append(patValue, scanner.Text())
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
	return patValue
}

func main() {
	pat, root := parse_args()
	visit := func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), "install.sh") || strings.HasSuffix(f.Name(), "install_nn.sh")) {
			grepped := grepFile(path, []byte(pat))
			fault := false
			for i := range grepped {
				com := strings.Trim(grepped[i], " ") //clean up the string, remove whitespace
				n := strings.LastIndex(com, " ") + 1 //index of next item after string
				l := len(com)
				if _, err := os.Stat(root + com[n:l-1]); os.IsNotExist(err) { //does the file exist
					if !fault { //is there a problem in this file, fault print file name once
						fmt.Printf("Problem with: %s\n", path)
						fault = true
					}
					fmt.Printf("  File: %s\n", root+com[n:l-1]) //substringing
				}
			}
		}
		return nil
	}
	fmt.Printf("Patern: %s Directory: %s\n", pat, root)
	err := filepath.Walk(root, visit)
	if err != nil {
		fmt.Printf("Done broke")
	}

}
