# [?] node: fix data race on httpConfig.prefix (#32047)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-06-16
Source: https://github.com/ethereum/go-ethereum/commit/9402187733c5b085a299c84a5aaf9e1fbd01e117
Type: security-commit

## Details
node: fix data race on httpConfig.prefix (#32047)

This fixes a data race when accessing the `httpConfig.prefix` field.
This field can be modified while the server is running through
`enableRPC`. The fix is storing the prefix in the handler, which is
accessed through the atomic pointer.

alternative to #32035
fixes https://github.com/ethereum/go-ethereum/issues/32019
