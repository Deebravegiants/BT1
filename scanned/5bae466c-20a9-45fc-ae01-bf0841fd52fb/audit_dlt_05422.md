# [?] Fix use after free accessing rodb cache nodes

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2025-07-10
Source: https://github.com/category-labs/monad/commit/07aa4f4461214cd447af6d58fe27603eb600d204
Type: security-commit

## Details
Fix use after free accessing rodb cache nodes

Since the ownership of the child nodes is implicitly implied by owning
the root node, share the node pointer only with requests that have the
same parent node. This will imply that they share root ownership as well
and can share the child pointer.

Add parent node to the key of inflights hash to ensure this property.
