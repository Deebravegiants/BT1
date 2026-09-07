# [?] chore: use latest wasmtime security patch (#15663)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-04
Source: https://github.com/near/nearcore/commit/d1f5a0f949a83f25d67729906aacec9b731c25b8
Type: security-commit

## Details
chore: use latest wasmtime security patch (#15663)

Update from wasmtime 36.0.7 to 36.0.8.

Related crates from the same monorepo are updated, too.

This includes a fix for a security advisory:
https://rustsec.org/advisories/RUSTSEC-2026-0114

We have `memory64` disabled, so we are not actually affected.

However, since we have not released anything with
Wasmtime, yet, it is still easy to update.
I don't really see a reason not to do it.
