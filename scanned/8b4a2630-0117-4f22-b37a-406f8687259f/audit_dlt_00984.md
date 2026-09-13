# [?] fix[lang]: method_id panic on non-constant (#5156)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-06-25
Source: https://github.com/vyperlang/vyper/commit/6f4ad4bb8dc541fbb544d6eeab340963996566e0
Type: security-commit

## Details
fix[lang]: method_id panic on non-constant (#5156)

method_id's arg is assumed to be a constant during codegen: `_try_fold` is
meant to constant-fold the call into a Bytes literal so codegen never
sees it. but `_try_fold` used `get_folded_value()`, which raises on non-
constant args; the folding pass swallows that exception, leaving codegen
to dispatch `MethodID.build_IR`, which doesn't exist — hence the
`CodegenPanic`.

use `reduced()` instead, which returns the original node when folding
fails. the existing `isinstance(value, vy_ast.Str)` guard then raises
`InvalidType` as intended, before codegen is reached.
