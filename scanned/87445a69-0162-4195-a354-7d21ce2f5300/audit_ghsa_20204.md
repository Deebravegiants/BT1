# [H] Data race in `Iter` and `IterMut`

## Summary
Severity: High
Advisory: GHSA-9hpw-r23r-xgm5
CWE: CWE-362
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-9hpw-r23r-xgm5
Type: github-advisory

## Affected
- crates.io: `thread_local` — affected >=0 <1.1.4

## Details
In the affected version of this crate, `{Iter, IterMut}::next` used a weaker memory ordering when loading values than what was required, exposing a potential data race
when iterating over a `ThreadLocal`'s values.

Crates using `Iter::next`, or `IterMut::next` are affected by this issue.

## References
- https://github.com/Amanieu/thread_local-rs/issues/33
- https://github.com/Amanieu/thread_local-rs
- https://rustsec.org/advisories/RUSTSEC-2022-0006.html
