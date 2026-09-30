# [C] Use of Uninitialized Resource in flumedb.

## Summary
Severity: Critical
Advisory: GHSA-p46c-w9m3-7qr2
CVE: CVE-2021-45684
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-p46c-w9m3-7qr2
Type: github-advisory

## Affected
- crates.io: `flumedb` — affected >=0 <0.1.6

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation. There are two of such cases (go_offset_log::read_entry() & offset_log::read_entry()).

Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45684
- https://github.com/sunrise-choir/flumedb-rs/issues/10
- https://github.com/sunrise-choir/flumedb-rs/pull/12
- https://github.com/sunrise-choir/flumedb-rs/commit/14b7440271c9d2316fab52c745e21087559364f6
- https://github.com/sunrise-choir/flumedb-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/flumedb/RUSTSEC-2021-0086.md
- https://rustsec.org/advisories/RUSTSEC-2021-0086.html
