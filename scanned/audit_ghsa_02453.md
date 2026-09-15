# [H] Data races in model

## Summary
Severity: High
Advisory: GHSA-mxv6-q98x-h958
CVE: CVE-2020-36460
CWE: CWE-362, CWE-843
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mxv6-q98x-h958
Type: github-advisory

## Affected
- crates.io: `model` — affected >=0

## Details
`Shared` data structure in `model` crate implements `Send` and `Sync` traits regardless of the inner type.
This allows safe Rust code to trigger a data race, which is undefined behavior in Rust.

Users are advised to treat `Shared` as an unsafe type.
It should not be used outside of the testing context,
and care must be taken so that the testing code does not have a data race
besides a race condition that is expected to be caught by the test.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36460
- https://github.com/spacejam/model/issues/3
- https://github.com/spacejam/model
- https://rustsec.org/advisories/RUSTSEC-2020-0140.html
