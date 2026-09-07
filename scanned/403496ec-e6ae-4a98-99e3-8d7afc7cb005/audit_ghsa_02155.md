# [H] Race condition in Parc

## Summary
Severity: High
Advisory: GHSA-xwxc-j97j-84gf
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-xwxc-j97j-84gf
Type: github-advisory

## Affected
- crates.io: `parc` — affected >=0

## Details
In the affected versions of this crate, `LockWeak<T>` unconditionally implemented `Send` with no trait bounds on `T`. `LockWeak<T>` doesn't own `T` and only provides `&T`. This allows concurrent access to a non-Sync `T`, which can cause undefined behavior like data races.

## References
- https://github.com/hyyking/rustracts/pull/6
- https://github.com/hyyking/rustracts/tree/master/parc
- https://rustsec.org/advisories/RUSTSEC-2020-0134.html
