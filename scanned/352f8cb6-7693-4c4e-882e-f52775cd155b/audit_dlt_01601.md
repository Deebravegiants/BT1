# [?] [decompiler] Fix VecPopBack pretty printing index out of bounds error

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-01-23
Source: https://github.com/MystenLabs/sui/commit/6023ccd1db7b147211eefeea1172c06dd42d6523
Type: security-commit

## Details
[decompiler] Fix VecPopBack pretty printing index out of bounds error

Fix bug where VecPopBack operation tried to access non-existent second
argument, causing "index out of bounds: the len is 1 but the index is 1"
errors during pretty printing

The pretty printer incorrectly assumed VecPopBack takes two arguments
(vector and value), when in fact it only takes one argument (the vector).

In `pretty_printer.rs:452-455`, the code was:

```rust
DataOp::VecPopBack(_) => maybe_parens(context, &args[0])
    .concat(D::text(".pop_back("))
    .concat(exp(context, &args[1]))  // args[1] doesn't exist!
    .concat(D::text(")")),
```

Changed to:

```rust
DataOp::VecPopBack(_) => maybe_parens(context, &args[0])
    .concat(D::text(".pop_back()")),
```

Now correctly generates: `vec.pop_back()` instead of crashing.

- Fixes 5.7% of decompilation failures on mainnet_most_used (64 packages)
- Example packages that failed 0x031d94b39cf6cd78c2d12edcc6684d0c27330dc0871a2536fe8ba913e586a5a6

All tests pass with no regressions.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
