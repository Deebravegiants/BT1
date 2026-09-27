# [?] rpc: fix handle batch deadlock (#22443)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-14
Source: https://github.com/erigontech/erigon/commit/c9d9061679963b91137f34cf1b475ce6142a5bb0
Type: security-commit

## Details
rpc: fix handle batch deadlock (#22443)

fixes #22424

Fix: wg.Add(len(calls)), matching the counter to the goroutines actually
spawned.
Added rpc/testdata/reqresp-batch-filtered.js using TDD (RED->GREEN)
