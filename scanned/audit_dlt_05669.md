# [?] VC: Fix assertion crash len(vc.forks) > 0. (#7862)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2026-01-21
Source: https://github.com/status-im/nimbus-eth2/commit/086b1b855251d4528091b98136e214f2bc555cf6
Type: security-commit

## Details
VC: Fix assertion crash len(vc.forks) > 0. (#7862)

* Add forks and preGenesis event conditions for block monitoring loop.
Add more comprehensive log statements for fork_service.

* Fix lint requirements.
