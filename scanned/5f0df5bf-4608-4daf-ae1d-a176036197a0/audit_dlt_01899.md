# [?] fix: BWIP race condition (#2405)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-07-09
Source: https://github.com/matter-labs/zksync-era/commit/8099ab0b77da3168a4184611adecb98a7d32fbaa
Type: security-commit

## Details
fix: BWIP race condition (#2405)

## What ❔

Separately insert proof_generation_details and gen data blob URLs.

## Why ❔

Sometimes BWIP generates data before insert_proof_generation_details is
called, which results in errors.

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.
