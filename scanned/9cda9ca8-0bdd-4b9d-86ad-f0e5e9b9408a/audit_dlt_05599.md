# [?] cmd/evm/internal/t8ntool: fix nil pointer dereference in Osaka blob gas calculation (#32714)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-09-23
Source: https://github.com/ethereum/go-ethereum/commit/2b5718fe9248fd9869a27408d31e8b59ef747315
Type: security-commit

## Details
cmd/evm/internal/t8ntool: fix nil pointer dereference in Osaka blob gas calculation (#32714)

The parent header was missing the BaseFee field when calculating the
reserve price for EIP-7918 in the Osaka fork, causing a nil pointer
dereference. This fix ensures BaseFee is properly set from ParentBaseFee
in the environment.

Added regression test case 34 to verify Osaka fork blob gas calculation
works correctly with parent base fee.
