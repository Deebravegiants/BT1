# [?] fix(rosetta): reject SECP256K1 keys instead of panicking (#15309)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-03-05
Source: https://github.com/near/nearcore/commit/940991dae5c243c92fd8fd27f7364629104f83f9
Type: security-commit

## Details
fix(rosetta): reject SECP256K1 keys instead of panicking (#15309)

The `/construction/payloads` endpoint panics when a SECP256K1 public key
is provided, crashing the entire neard process.

This PR fixes the incorrect behavior. Now requests with unsupported key
types return `{"code":400,"message":"Invalid Input: SECP256K1 keys are
not supported in Rosetta","retryable":false}` and the panic is not
triggered.
