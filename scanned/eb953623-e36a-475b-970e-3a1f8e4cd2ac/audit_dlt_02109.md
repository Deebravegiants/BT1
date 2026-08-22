# [?] fix(fmt): don't break exprs that overflow but fit assignement (#11837)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-09-29
Source: https://github.com/foundry-rs/foundry/commit/fef41c115db9912033de8e484dee53359762e236
Type: security-commit

## Details
fix(fmt): don't break exprs that overflow but fit assignement (#11837)

* fix(fmt): don't break exprs that overflow but fit assignement

* fix(fmt): account for bin operators in `fn estimate_size`

* fix(CI): disable win test for 0x-settler to avoid panic

---------

Co-authored-by: grandizzy <38490174+grandizzy@users.noreply.github.com>
Co-authored-by: grandizzy <grandizzy.the.egg@gmail.com>
