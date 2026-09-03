# [?] fix(tee): correct previous fix for race condition in batch locking (#3358)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-12-04
Source: https://github.com/matter-labs/zksync-era/commit/b12da8d1fddc7870bf17d5e08312d20773815269
Type: security-commit

## Details
fix(tee): correct previous fix for race condition in batch locking (#3358)

## What ❔

Commit a7dc0ed5007f6b2f789f4c61cb3d137843151860 (PR #3342) was supposed
to fix a race condition in batch locking by introducing SQL row-locking,
but it [didn't work][2] as expected.
![Screenshot From 2024-12-04
11-32-32](https://github.com/user-attachments/assets/959ffc3c-593f-409a-87ab-68ec197040a0)
Now we are switching back to coarser-grained table-level locking as
[originally suggested][1] by Harald. The original fix was hard to test
unless deployed to `stage` due to the undeterministic nature of the
problem, so we needed to merge it to the `main` branch to properly test
it.

[1]:
https://github.com/matter-labs/zksync-era/pull/3342#issuecomment-2514573386
[2]: https://grafana.matterlabs.dev/goto/AhEd5FVNg?orgId=1

## Why ❔

To fix the bug that only activates after running `zksync-tee-prover` on
multiple instances.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.
