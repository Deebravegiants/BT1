# [H] CL-2021-23: Prysm integer square root bug

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
package main

import (
	"encoding/binary"
	"fmt"
	"math"
	"math/big"
)

// The largest integer x such that x**2 is less than or equal to n.
func IntegerSquareroot(n uint64) uint64 {
	x := n
	y := (x + 1) >> 1
	for y < x {
		x = y
		y = (x + n/x) >> 1
	}
	return x
}

// ----------------- Prysm code -------------------------

// Common square root values.
var squareRootTable = map[uint64]uint64{
	4:       2,
	16:      4,
	64:      8,
	256:     16,
	1024:    32,
	4096:    64,
	16384:   128,
	65536:   256,
	262144:  512,
	1048576: 1024,
	4194304: 2048,
}

// IntegerSquareRoot defines a function that returns the

_Trimmed to 38 lines — full report: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md_
