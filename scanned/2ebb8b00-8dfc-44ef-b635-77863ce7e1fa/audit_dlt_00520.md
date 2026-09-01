# [?] fix: fix race condition in FullPruningDb read methods (#10920)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-02
Source: https://github.com/NethermindEth/nethermind/commit/afddfd76f4c6cf5ca36be76e515cd7cffbaa8181
Type: security-commit

## Details
fix: fix race condition in FullPruningDb read methods (#10920)

* Update FullPruningDb.cs

* Update FullPruningDb.cs

* Update FullPruningDb.cs

* fix: capture _pruningContext locally in StartWriteBatch

Same race-condition class as the read methods: the field is read twice
in the ternary, so a concurrent FinishPruning clearing it to null between
the null check and the .CloningDb dereference would throw NRE.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* Apply suggestion from @LukaszRozmej

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>
Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
