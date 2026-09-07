# [?] accounts/abi: fix panic when check event with log has empty or nil topics (#32503)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-08-27
Source: https://github.com/ethereum/go-ethereum/commit/52ec2b5f47ca899a35df1bd9b03750dc2db6f2a9
Type: security-commit

## Details
accounts/abi: fix panic when check event with log has empty or nil topics (#32503)

When the log has empty or nil topics, the generated bindings code will
panic when accessing `log.Topics[0]`, add a check to avoid it.
