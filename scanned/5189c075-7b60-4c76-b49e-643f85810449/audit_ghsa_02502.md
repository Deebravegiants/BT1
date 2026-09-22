# [H] Data race in ruspiro-singleton

## Summary
Severity: High
Advisory: GHSA-fqq2-xp7m-xvm8
CVE: CVE-2020-36435
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fqq2-xp7m-xvm8
Type: github-advisory

## Affected
- crates.io: `ruspiro-singleton` — affected >=0 <0.4.1

## Details
`Singleton<T>` is meant to be a static object that can be initialized lazily. In
order to satisfy the requirement that `static` items must implement `Sync`,
`Singleton` implemented both `Sync` and `Send` unconditionally.

This allows for a bug where non-`Sync` types such as `Cell` can be used in
singletons and cause data races in concurrent programs.

The flaw was corrected in commit `b0d2bd20e` by adding trait bounds, requiring
the contaiend type to implement `Sync`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36435
- https://github.com/RusPiRo/ruspiro-singleton/issues/10
- https://github.com/RusPiRo/ruspiro-singleton/pull/11
- https://github.com/RusPiRo/ruspiro-singleton/commit/b0d2bd20eb40b9cbc2958b981ba2dcd9e6f9396e
- https://github.com/RusPiRo/ruspiro-singleton
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ruspiro-singleton/RUSTSEC-2020-0115.md
- https://rustsec.org/advisories/RUSTSEC-2020-0115.html
