# [?] Fix panic in ethstats when block state is unavailable (#1778)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-12-18
Source: https://github.com/celo-org/celo-blockchain/commit/a0117f54daf8524a2be59e4e62a8b3f0442e2477
Type: security-commit

## Details
Fix panic in ethstats when block state is unavailable (#1778)

* check error from getting statedb for a block to avoid panic

* add a warning log statement

* 🤦

* Update ethstats/ethstats.go

Co-authored-by: piersy <pierspowlesland@gmail.com>

* remove unessasary change

Co-authored-by: piersy <pierspowlesland@gmail.com>
Co-authored-by: Gaston Ponti <pontigaston@gmail.com>
