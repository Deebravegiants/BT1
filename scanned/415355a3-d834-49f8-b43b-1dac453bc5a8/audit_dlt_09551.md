# [?] also remove RUSTSEC-2021-0139.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-02-25
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f3df553220b38ed570bd2011f515cfd61d6a99c2
Type: security-commit

## Details
also remove RUSTSEC-2021-0139.

## Patch
### deny.toml
```diff
@@ -81,7 +81,6 @@ ignore = [
     "RUSTSEC-2020-0016", # net2 unmaintained
     "RUSTSEC-2024-0384", # instant unmaintained
     "RUSTSEC-2024-0388", # derivative unmaintained
-    "RUSTSEC-2021-0139", # ansi_term unmaintained
     "RUSTSEC-2025-0056", # adler is unmaintained, use adler2 instead
     "RUSTSEC-2025-0137", # https://github.com/rustsec/advisory-db/pull/2538#issuecomment-3684201405
 ]
```
