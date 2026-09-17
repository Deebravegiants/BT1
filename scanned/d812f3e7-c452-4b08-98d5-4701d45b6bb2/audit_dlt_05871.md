# [?] fix(zk_toolbox): Do not panic if mint is not successful (#2973)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-09-26
Source: https://github.com/matter-labs/zksync-era/commit/57b99d4fc906ae7ab5532ea23a069b34a2ee7c02
Type: security-commit

## Details
fix(zk_toolbox): Do not panic if mint is not successful (#2973)

## What ❔

Use governor for minting process and do not panic if minting is not
successful

## Why ❔

<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [ ] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [ ] Code has been formatted via `zk fmt` and `zk lint`.

Signed-off-by: Danil <deniallugo@gmail.com>
