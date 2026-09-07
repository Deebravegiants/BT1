# [H] Go Ethereum Improper Input Validation

## Summary
Severity: High
Chain: Ethereum
Component: github.com/ethereum/go-ethereum
CVE: CVE-2018-16733
CWE: Improper Input Validation
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-qr2j-wrhx-4829
Type: github-advisory

## Details
In Go Ethereum (aka geth) before 1.8.14, TraceChain in eth/api_tracer.go does not verify that the end block is after the start block.

### Specific Go Packages Affected
github.com/ethereum/go-ethereum/eth
