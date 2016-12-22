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
func grepFile(path, file string, pat []byte) {
	//var patValue []string //don't know how efficient 0 len slice is
	f, err := os.Open(file)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		if bytes.Contains(scanner.Bytes(), pat) {
			//patValue = append(patValue, scanner.Text())
			command := strings.Trim(scanner.Text(), " ") //clean out extra whitespace
			n := strings.LastIndex(command, " ") + 1     //index of next item after string
			l := len(command)
			if n >= l-1 {
				fmt.Printf("Scanner:%s\n\tn: %v l: %v \n", command, n, l)
			}
			if _, err := os.Stat(path + command[n:l-1]); os.IsNotExist(err) { //see if the file exists
				fmt.Printf("\tNo dice: %s%s\n", path, command[n:l-1])
			}
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
}

func main() {
	file, pat, root := parse_args()
	visit := func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), "install.sh") || strings.HasSuffix(f.Name(), "install_nn.sh")) {
			fmt.Printf("Checking: %s\n", path)
			grepFile(root, path, []byte(pat))
			//		for i := range grepped {
			//			n := strings.LastIndex(grepped[i], " ") + 1 //index of next item after string
			//			l := len(grepped[i])
			//			fmt.Println("\t", grepped[i][n:l-1])
			//		}
		}
		return nil
	}
	grepFile(root, file, []byte(pat))
	err := filepath.Walk(root, visit)
	if err != nil {
		fmt.Printf("Done broke")
	}

}
