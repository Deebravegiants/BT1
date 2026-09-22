# [?] accounts/abi/bind: fix data race in TestWaitDeployedCornerCases (#32740)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-09-25
Source: https://github.com/ethereum/go-ethereum/commit/7611f351c18de983c49544f09aa042bd0403243b
Type: security-commit

## Details
accounts/abi/bind: fix data race in TestWaitDeployedCornerCases (#32740)

Fixes race in WaitDeploy test where the backend is closed before goroutine using it wraps up.

---------

Co-authored-by: lightclient <lightclient@protonmail.com>
