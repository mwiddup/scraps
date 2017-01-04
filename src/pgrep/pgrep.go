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

func parse_args() (pat string, path string) {
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

//basic grep functionallity, returns a slice of each matched line
//no filtering or utilities performed
func grepFile(file string, pat []byte) Results {
	var patValue Results
	var myPat []patLine //this is the 0 length slice
	//patValue.patLine = make([]patLine, 0)
	//myPat := patLine{file: scanner.Text(), line: i}
	start := time.Now()
	f, err := os.Open(file)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	i := 0
	for scanner.Scan() {
		i++
		if bytes.Contains(scanner.Bytes(), pat) {
			myPat = append(myPat, patLine{file: scanner.Text(), line: i})
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
	patValue.elapsed = time.Since(start)
	patValue.patLine = myPat
	return patValue
}

func main() {
	checkFiles()
}

func checkFiles() {
	pat, root := parse_args()
	allPass := true
	visit := func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), "install.sh") || strings.HasSuffix(f.Name(), "install_nn.sh")) {
			grepped := grepFile(path, []byte(pat))
			fault := false
			fmt.Printf("=== RUN   %s\n", path)
			for i := range grepped.patLine {
				com := strings.Trim(grepped.patLine[i].file, " ") //clean up the string, remove whitespace
				lne := grepped.patLine[i].line
				tme := grepped.elapsed
				n := strings.LastIndex(com, " ") + 1 //index of next item after string
				l := len(com)
				if _, err := os.Stat(root + com[n:l-1]); os.IsNotExist(err) { //does the file exist
					if !fault { //is there a problem in this file, fault print file name once
						//fmt.Printf("=== RUN   %s\n", path)
						fmt.Printf("--- FAIL: %s (%s)\n", path, tme)
						fault = true
						allPass = false
					}
					fmt.Printf("\tFile:%03d: %s\n", lne, root+com[n:l-1]) //substringing
				}
			}
			if !fault {
				fmt.Printf("--- PASS: %s (0.00s)\n", path)
			}
		}
		return nil
	}
	err := filepath.Walk(root, visit)
	if err != nil {
		fmt.Printf("Done broke")
	}
	if !allPass {
		fmt.Printf("FAIL\nexit status 1\nFAIL     Check Files\t0.008s\n")
	}

}
