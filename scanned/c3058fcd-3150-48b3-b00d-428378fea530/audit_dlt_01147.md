# [?] eth/tracers/native: prevent panic for LOG edge-cases (#26848)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-03-28
Source: https://github.com/ethereum/go-ethereum/commit/fd94b4fcfa244179c0500b70fb2944cb686b9ca4
Type: security-commit

## Details
eth/tracers/native: prevent panic for LOG edge-cases (#26848)

This PR fixes OOM panic in the callTracer as well as panicing on
opcode validation errors (e.g. stack underflow) in callTracer and
prestateTracer.

Co-authored-by: Martin Holst Swende <martin@swende.se>
