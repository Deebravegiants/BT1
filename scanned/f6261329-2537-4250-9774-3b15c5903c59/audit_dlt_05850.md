# [?] fix: allow panic_with_no_subnet_record in //rs/tests/nns:delete_subnet_test (#10039)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-04-28
Source: https://github.com/dfinity/ic/commit/fd0179fced559f5c9c8d074ff3440386404e7b8c
Type: security-commit

## Details
fix: allow panic_with_no_subnet_record in //rs/tests/nns:delete_subnet_test (#10039)

The `//rs/tests/nns:delete_subnet_test` would sometimes flake with:
```
Task assert_no_unallowed_log_patterns FAILED  in   0.13s
     Found unallowed log patterns in IC logs for group `delete-subnet-test--1777304524162056`:
     - Pattern `panicked`: 4 match(es)
         [2026-04-27T15:44:03.888270Z qis6x-cqfp3-tdpzb-xff7d-veukd-t6q63-dzqjb-2dbdf-jnoxu-gmqsg-tae] thread 'consensus_Processor' (1450) panicked at rs/consensus/src/consensus.rs:357:17:
         [2026-04-27T15:44:05.112477Z kouz2-swfzy-zjmx6-emb7x-keyk5-pwqzk-iqvsa-cdlhp-3kred-zk74b-gqe] thread 'consensus_Processor' (1448) panicked at rs/consensus/src/consensus.rs:357:17:
         [2026-04-27T15:44:03.888810Z vs5cs-seu3u-e365w-ksb63-lin7b-2m7ll-4jx54-hlpsz-bab5j-ksn2c-bqe] thread 'consensus_Processor' (1387) panicked at rs/consensus/src/consensus.rs:357:17:
         ... and 1 more
```
This is because subnet deletion deletes the subnet record. The replica
currently panics if it notices the missing subnet record before it is
killed by the orchestrator. The reason it's flaky is because the panic
races against the orchestrator killing the replica. If the panic is
first we hit the flake, if the orchestrator kills the replica first the
test passes.

We fix this by allowing the specific `panic_with_no_subnet_record` in
the `delete_subnet_test`.
