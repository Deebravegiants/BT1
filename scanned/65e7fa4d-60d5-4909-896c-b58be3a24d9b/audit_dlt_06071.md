# [?] fix: panic when sending funds to invalid address (#3457)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-12-05
Source: https://github.com/penumbra-zone/penumbra/commit/ab12795f58ea69b21736ebd593f45152416f1cea
Type: security-commit

## Details
fix: panic when sending funds to invalid address (#3457)

* crypto: add method to infallibly expand `ClueKey`

* fix: expand clue key infallibly when creating clues (closes #3332)

* test: invalid clue keys should expand infallibly
