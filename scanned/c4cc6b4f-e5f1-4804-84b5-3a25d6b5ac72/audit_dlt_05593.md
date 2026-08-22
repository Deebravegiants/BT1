# [?] eth/tracers: fix data race on interruption reason across tracers (#34827)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-05-11
Source: https://github.com/ethereum/go-ethereum/commit/22919cec1b257b3f2d3a2c348f432c08efae7114
Type: security-commit

## Details
eth/tracers: fix data race on interruption reason across tracers (#34827)

Every tracer that implements Stop/GetResult held a `reason error` field
that is written by Stop (called from the trace-timeout watchdog
goroutine in api.go) and read by GetResult (called by the RPC handler
main goroutine). These accesses were unsynchronized.
