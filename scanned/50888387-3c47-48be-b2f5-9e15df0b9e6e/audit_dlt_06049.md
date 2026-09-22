# [?] Fix non-deterministic tests (#944)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2026-04-06
Source: https://github.com/kaspanet/rusty-kaspa/commit/3be6630fea6eccc87c906b632f3cd1ec2152907a
Type: security-commit

## Details
Fix non-deterministic tests (#944)

* Increase SYNC_MAX_DELAY

* Increase mine_block timeout duration

* Increase test_writer_reentrance timeout

* Ignore underflows when dropping a UtxosChangedSubscription

* Fix integration tests to use 100 as FD limit

* Make TEST_FD_LIMIT maximum for tests, in case OS limit is lower

* Remove OS free port allocation and just use a random port instead

* clippy

* Increase timeout_duration for mine_block
