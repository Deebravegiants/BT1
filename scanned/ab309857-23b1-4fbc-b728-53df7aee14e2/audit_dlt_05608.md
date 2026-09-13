# [?] eth/tracers: avoid panic in state test runner (#30332)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-08-21
Source: https://github.com/ethereum/go-ethereum/commit/30824faf90bf5d1f5e4a1cf0b50de80f10d16490
Type: security-commit

## Details
eth/tracers: avoid panic in state test runner (#30332)

Make tracers more robust by handling `nil` receipt as input. 
Also pass in a receipt with gas used in the state test runner.
Closes https://github.com/ethereum/go-ethereum/issues/30117.

---------

Co-authored-by: Sina Mahmoodi <itz.s1na@gmail.com>
