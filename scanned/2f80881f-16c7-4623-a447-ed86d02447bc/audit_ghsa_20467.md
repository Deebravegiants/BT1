# [C] Use of Uninitialized Resource in csv-sniffer.

## Summary
Severity: Critical
Advisory: GHSA-9783-42pm-x5jq
CVE: CVE-2021-45686
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9783-42pm-x5jq
Type: github-advisory

## Affected
- crates.io: `csv-sniffer` — affected >=0 <0.2.0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation (within fn preamble_skipcount()).

Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45686
- https://github.com/jblondin/csv-sniffer/issues/1
- https://github.com/jblondin/csv-sniffer/pull/2
- https://github.com/jblondin/csv-sniffer
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/csv-sniffer/RUSTSEC-2021-0088.md
- https://rustsec.org/advisories/RUSTSEC-2021-0088.html
