# [?] fix: subtraction overflow computation bug (#579)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys/gnark
Published: 2023-03-16
Source: https://github.com/Consensys/gnark/commit/0e81df4897a3d1617a559dccca7bfa959a23eb55
Type: security-commit

## Details
fix: subtraction overflow computation bug (#579)

* feat: add subtraction without inline reduction

* fix: count possible overflow due to subtraction padding

Previously when estimating the maximal overflow for subtraction we only
considered the possible overflow caused by the subtraction padding and the
subtrahend. But actually as the padding may overflow the minuend we have to
also consider it.

Due to this, we also had to decrease the maximal possible overflow by one as
modular reduction uses subtraction as a subroutine.

* test: update circuit statistics

* fix: remove empty branch
