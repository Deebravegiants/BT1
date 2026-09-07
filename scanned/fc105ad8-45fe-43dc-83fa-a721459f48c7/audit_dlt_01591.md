# [?] [compiler] Fixing cyclic type replacement leading to stack overflow (#16473)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-04-27
Source: https://github.com/aptos-labs/aptos-core/commit/5a9898905a88e7b30300076a11af0556730fae50
Type: security-commit

## Details
[compiler] Fixing cyclic type replacement leading to stack overflow (#16473)

* [compiler] Fixing a bug in inferred type defaults

Inferred type defaults where not checked for abilities. Closes #16405

* [compiler] Fixing cyclic type replacement leading to stack overflow

When creating default types from constraints during type finalization we can run into cycles, leading to stack overflow. This adds a visiting set to the replacement algorithm to bail out in this case.

Closes #16435

* Update comment.
