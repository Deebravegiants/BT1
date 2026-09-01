# [?] Fix race condition in ShutterBlockHandler (#10296)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-01-30
Source: https://github.com/NethermindEth/nethermind/commit/8d695ffdade80c0271bb673abe89aa881142f2e5
Type: security-commit

## Details
Fix race condition in ShutterBlockHandler (#10296)

* fix(shutter): add synchronization to CancelWaitForBlock to prevent race condition

* Add lock to Dispose

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

* Fix Dispose lock

* Fix test for async TCS completion

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>
