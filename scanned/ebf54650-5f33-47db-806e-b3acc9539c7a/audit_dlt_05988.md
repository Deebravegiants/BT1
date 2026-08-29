# [?] build(store): repin cronos-store to fix historical-query use-after-free and merge-iterator overhead (#2181)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2026-08-07
Source: https://github.com/crypto-org-chain/cronos/commit/7aa5afe37285c07e52f27ed92b794e656875744e
Type: security-commit

## Details
build(store): repin cronos-store to fix historical-query use-after-free and merge-iterator overhead (#2181)

* build: repin cronos-store to crypto-org-chain/cronos-store#110

Picks up the historical-query zero-copy use-after-free fix and the
merge-iterator copy-overhead fix.

* docs: add changelog entry for cronos-store repin

* build: bump cronos-store pin to PR#110 branch head

Picks up the golangci-lint import-grouping/spelling fixup commit.

* docs: cover merge-iterator perf fix in changelog entry

* fix(store): tidy go.sum for cosmos-sdk repin, trim changelog entry

go.sum was missing entries for the newer cosmos-sdk pseudo-version,
failing golangci-lint and unittest CI. Also merge the duplicate Chores
header and trim the #2181 changelog line per review feedback.

---------

Signed-off-by: JayT106 <JayT106@users.noreply.github.com>
