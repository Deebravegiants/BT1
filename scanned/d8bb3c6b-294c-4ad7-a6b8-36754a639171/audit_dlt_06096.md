# [?] Fix MockProver `assert_verify` panic errors (#118)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-scaling-explorations/halo2
Published: 2023-01-09
Source: https://github.com/privacy-ethereum/halo2/commit/be10b68d4b704de8a6639fb201fcf20a7f3e3c62
Type: security-commit

## Details
Fix MockProver `assert_verify` panic errors (#118)

* fix: Support dynamic lookups in `MockProver::assert_verify`

Since lookups can only be `Fixed` in Halo2-upstream, we need to add
custom suport for the error rendering of dynamic lookups which doesn't
come by default when we rebase to upstream.

This means that now we have to print not only `AdviceQuery` results to
render the `Expression` that is being looked up. But also support
`Instance`, `Advice`, `Challenge` or any other expression types that are
avaliable.

This addresses the rendering issue, renaming also the `table_columns`
variable for `lookup_columns` as the columns do not have the type
`TableColumn` by default as opposite to what happens upstream.

* fix: Don't error and emit empty String for Empty queries

* feat: Add `assert_sarisfied_par` fn to `MockProver`

* fix: Address clippy errors

* chore: Address review comments

* chore: Fix clippy lints

Resolves: #116
