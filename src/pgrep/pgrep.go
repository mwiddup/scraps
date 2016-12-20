// Some guy called Peter made this. Found on the internet, no known author
// maybe github/lmmx/  -- but probably not
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

func parse_args() (file, pat string, path string) {
	if len(os.Args) < 3 {
		log.Fatal("usage: pgrep <file_name> <pattern>")
	}
	file = os.Args[1]
	pat = os.Args[2]
	path = os.Args[3]
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

func visit(path string, f os.FileInfo, err error) error {
	if !f.IsDir() && (strings.HasSuffix(f.Name(), "install.sh") || strings.HasSuffix(f.Name(), "install_nn.sh")) {
		fmt.Printf("Visited: %s\n", path)
	}
	return nil
}

func main() {
	file, pat, root := parse_args()
	grepped := grepFile(file, []byte(pat))
	for i := range grepped {
		n := strings.LastIndex(grepped[i], " ") + 1 //index of next item after string
		l := len(grepped[i])
		fmt.Println(grepped[i][n : l-1])
	}
	err := filepath.Walk(root, visit)
	fmt.Printf("filepath.Walk() returned %v\n", err)
}
