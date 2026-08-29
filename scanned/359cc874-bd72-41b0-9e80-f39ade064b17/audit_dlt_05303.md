# [?] fix(core): reject amount addition overflow (#8686)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-06-12
Source: https://github.com/fedimint/fedimint/commit/25ef880c3af703d14b4a18f316053825306f8173
Type: security-commit

## Details
fix(core): reject amount addition overflow (#8686)

Summary

Reject overflows when combining multi-unit amount maps.

Details

`Amounts::checked_add` delegated to `checked_add_mut` but ignored a
`None` result, so callers could observe `Some` even when adding an
amount overflowed. Propagate the overflow result so funding checks and
other callers fail closed.

This also adds a regression test covering an output plus fee overflow in
the funding verifier.

Testing

- `cargo test -p fedimint-server
consensus::transaction::tests::funding_verifier_rejects_output_plus_fee_overflow`
- `just final-lint`
