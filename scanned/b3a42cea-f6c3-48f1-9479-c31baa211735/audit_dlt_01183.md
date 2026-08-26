# [?] Fixes #9577: resolve race condition in StateSyncFeedTests.Big_test (#9972)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-12-29
Source: https://github.com/NethermindEth/nethermind/commit/fee0f239e070415f598cd4c9a382d656479640ea
Type: security-commit

## Details
Fixes #9577: resolve race condition in StateSyncFeedTests.Big_test (#9972)

* fix(sync): resolve race condition in StateSyncFeedTests.Big_test (#9577)

* fix(sync): Isolate block tree cache in StateSyncFeedTestsBase to fix parallel test failures

* changes

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>
