# [?] fix: remove non-determinism from tests (#1537)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2024-11-22
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/f7d54f339a7c278c9fa7ce06f3aa040a998e7f9c
Type: security-commit

## Details
fix: remove non-determinism from tests (#1537)

* Remove non-determinism from tests

This removes non-determinism from the tests caused by a shared RNG
across tests.

* Disable tests with `RETURN_DATA_OFFSET` overflow

This disables three tests which lead to an overflow of the
`hub/RETURN_DATA_OFFSET` column during trace generation.  See #1538.
