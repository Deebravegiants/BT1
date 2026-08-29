# [?] fix(en): Do not crash node in sync state updater task (#4247)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-15
Source: https://github.com/matter-labs/zksync-era/commit/7bc1f12998a5444f6be1988a670944da8bab5b38
Type: security-commit

## Details
fix(en): Do not crash node in sync state updater task (#4247)

## What ❔

Fixes node crashing if the main node is inaccessible when updating the
node sync state.

## Why ❔

Crashing the node in this case looks disproportionate.

## Is this a breaking change?

- [ ] Yes
- [x] No

## Operational changes

No operational changes.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

---------

Co-authored-by: Danil Lugovskoi <dl@matterlabs.dev>
Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
