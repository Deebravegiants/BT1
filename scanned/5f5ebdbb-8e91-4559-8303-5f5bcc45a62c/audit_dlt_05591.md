# [?] core: fix tracer panic (#35396)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-07-22
Source: https://github.com/ethereum/go-ethereum/commit/5d88c6b324b69f391e2677f13e5eae4493eefb4b
Type: security-commit

## Details
core: fix tracer panic (#35396)

Now with 8037, there are transactions that fail AFTER intrinsic gas but
BEFORE Call or Create operation. These will currently result in a panic
in tracing, since they produce a receipt

---------

Co-authored-by: Gary Rong <garyrong0905@gmail.com>
