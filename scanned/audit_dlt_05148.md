# [?] Add LSPS5 DOS protections.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-08-07
Source: https://github.com/lightningdevkit/rust-lightning/commit/4370cffdb011f2bfadaa32a66e989c3c8f70feb0
Type: security-commit

## Details
Add LSPS5 DOS protections.

When handling an incoming LSPS5 request, the manager will check
if the counterparty is 'engaged' in some way before responding.
`Engaged` meaning = active channel | LSPS2 active operation | LSPS1 active operation.

Logic: `If not engaged then reject request;`

A single test is added only checking for the active channel condition,
because it's not super easy to get LSPS1-2 on the correct state to check this (yet).
Other tangential work is happening that will make this easier and more tests will come in the near future
