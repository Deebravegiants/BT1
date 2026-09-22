# [C] IO FinNet tss-lib vulnerable to timing attack from non-constant time scalar multiplication

## Summary
Severity: Critical
Chain: github.com/bnb-chain/tss-lib
Component: github.com/bnb-chain/tss-lib, github.com/binance-chain/tss-lib
CVE: CVE-2023-26556
CWE: Observable Discrepancy
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-3w84-4mjc-rjw7
Type: github-advisory

## Details
io.finnet tss-lib before 2.0.0 can leak a secret key via a timing side-channel attack because it relies on the scalar-multiplication implementation in Go crypto/elliptic, which is not constant time (there is an if statement in a loop). One leak is in ecdsa/keygen/round_2.go. (bnb-chain/tss-lib and thorchain/tss are also affected.)
