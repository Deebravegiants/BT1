# [?] Fix race condition in consensus.State code (#673)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2023-04-11
Source: https://github.com/cometbft/cometbft/commit/6a96eca67fb810aa823e9de4da41cc8028637a65
Type: security-commit

## Details
Fix race condition in consensus.State code (#673)

* Repro in e2e tests

* Change something in the code

* Fix race condition in `SwitchToConsensus`

* Revert "Repro in e2e tests"

This reverts commit 4f441f8ebac8f245d5a641c25ccdfa3b382ca063.

* RAII lock
