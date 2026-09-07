# [?] Fix race condition in `gossipVotesRoutine` (#692)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2023-04-11
Source: https://github.com/cometbft/cometbft/commit/85441ab257a01ba904fdf62b5da33e7e6e9c5b5a
Type: security-commit

## Details
Fix race condition in `gossipVotesRoutine` (#692)

* Repro in e2e tests

* Increase chances of data race

* Exacerbate race condition (2nd try)

* Fix race condition in `gossipVotesRoutine`

* Revert logic to expose data race

* RAII lock
