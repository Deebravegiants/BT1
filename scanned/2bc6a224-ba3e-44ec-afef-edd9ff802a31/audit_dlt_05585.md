# [?] fix: use platform independent method for counting new multiplication overflow from result limb count (#916)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys/gnark
Published: 2023-11-15
Source: https://github.com/Consensys/gnark/commit/5c18f4540c0735a71db71cceee77c6c8f714c2a8
Type: security-commit

## Details
fix: use platform independent method for counting new multiplication overflow from result limb count (#916)

* fix: use bits.Len for universal computation of multiplication overflow

* fix: handle edge case in multiplication limb count

* fix: define default number of limbs in div and inv precond
