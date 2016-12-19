// install-files.go
// This should cycle through the install scripts and pull out the
// objects referenced then check those objects exist

package main

import (
	"bufio"
	"fmt"
	"io"
	"io/ioutil"
	"os"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {

	dat, err := ioutil.ReadFile("/tmp/dat")
	check(err)
	fmt.Print(sting(dat))

	f, err := os.Open("/tmp/dat")
	check(err)
	fmt.Printf("%d bytes: %s\n", n1, string(b1))

	o2, err := f.Seek(6, 0)
	check(err)
	b2 := make([]byte, 2)
}
