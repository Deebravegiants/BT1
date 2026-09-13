# [?] Fix data race: roundChangeTimer (#1659)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-08-09
Source: https://github.com/celo-org/celo-blockchain/commit/f82aa14059c9b1f210077123df2700b4c912f6f4
Type: security-commit

## Details
Fix data race: roundChangeTimer (#1659)

### Description

Add Mu to deal with data race around roundChangeTimer.

### Other changes

None

### Tested

`go test -race ./e2e_test` doesn't return data races on roundChangeTimer.

CI

### Related issues

- Fixes #1587 

### Backwards compatibility

Yes
