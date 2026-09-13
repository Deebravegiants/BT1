# [?] util: introduce `TrySub` to prevent unsigned underflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-02-22
Source: https://github.com/bitcoin/bitcoin/commit/b8fa6f0f701f04cffca6a085337b508381016649
Type: security-commit

## Details
util: introduce `TrySub` to prevent unsigned underflow

Introduce `TrySub(T&, U)` which subtracts an unsigned integral `U` from an unsigned integral `T`, returning `false` on underflow.
Use with `Assume(TrySub(...))` at coins cache accounting decrement sites so invariant violations fail immediately rather than silently wrapping.

Co-authored-by: MarcoFalke <*~=`'#}+{/-|&$^_@721217.xyz>
Co-authored-by: Pieter Wuille <pieter@wuille.net>
