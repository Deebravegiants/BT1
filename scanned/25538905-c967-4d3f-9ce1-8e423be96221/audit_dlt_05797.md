# [?] fix: avoid panic when migrate param for newly added host (#6167)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2024-04-22
Source: https://github.com/cosmos/ibc-go/commit/c4413c5877f9ef883494da1721cb18caaba7f7f5
Type: security-commit

## Details
fix: avoid panic when migrate param for newly added host (#6167)

* fix: avoid panic when migrate param for newly added host

* keep default params

* Apply suggestions from code review

* allow use default params when set nil legacySubspace

* Update CHANGELOG.md

Co-authored-by: coderabbitai[bot] <136622811+coderabbitai[bot]@users.noreply.github.com>

* Update CHANGELOG.md

* cleanup

* refactor: rm setter in icahost migrator and adjust test case

* chore: update changelog

* Apply suggestions from code review

* Apply suggestions from code review

* Apply suggestions from code review

---------

Co-authored-by: Carlos Rodriguez <carlos@interchain.io>
Co-authored-by: coderabbitai[bot] <136622811+coderabbitai[bot]@users.noreply.github.com>
Co-authored-by: Damian Nolan <damiannolan@gmail.com>
