# [H] Data races in parc

## Summary
Severity: High
Advisory: GHSA-29v7-3v4c-gf38
CVE: CVE-2020-36454
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-29v7-3v4c-gf38
Type: github-advisory

## Affected
- crates.io: `parc` — affected >=0

## Details
In the affected versions of this crate, LockWeak<T> unconditionally implemented Send with no trait bounds on T. LockWeak<T> doesn't own T and only provides &T. This allows concurrent access to a non-Sync T, which can cause undefined behavior like data races.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36454
- https://github.com/hyyking/rustracts/pull/6
- https://github.com/hyyking/rustracts/tree/master/parc
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/parc/RUSTSEC-2020-0134.md
- https://rustsec.org/advisories/RUSTSEC-2020-0134.html
