# [?] fix(api): Fix panic applying nonce override (#3748)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2025-03-24
Source: https://github.com/matter-labs/zksync-era/commit/944059b0cb2911debc3253a3066c4ce855b5196b
Type: security-commit

## Details
fix(api): Fix panic applying nonce override (#3748)

## What ❔

- Refactors state override application in the API server.
- Adds metrics related to state overrides.

## Why ❔

Currently, `eth_call` / `eth_estimateGas` will panic if a nonce override
is supplied. This is because in this case, storage is read using
blocking `ReadStorage` trait in the non-blocking context.

## Is this a breaking change?

- [ ] Yes
- [x] No

## Operational changes

No operational changes.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.
