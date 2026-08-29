# [?] ethdb/pebble: prevent shutdown-panic (#27238)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-05-19
Source: https://github.com/etclabscore/core-geth/commit/99394adcb8e5d2708e773b838dc92b4a0896ed2d
Type: security-commit

## Details
ethdb/pebble: prevent shutdown-panic (#27238)

One difference between pebble and leveldb is that the latter returns error when performing Get on a closed database, the former does a panic. This may be triggered during shutdown (see #27237)

This PR changes the pebble driver so we check that the db is not closed already, for several operations. It also adds tests to the db test-suite, so the previously implicit assumption of "not panic:ing at ops on closed database" is covered by tests.
