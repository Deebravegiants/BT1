# [H] Format string vulnerabilities in pancurses

## Summary
Severity: High
Advisory: GHSA-m57c-4vvx-gjgq
CVE: CVE-2019-15546
CWE: CWE-134
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m57c-4vvx-gjgq
Type: github-advisory

## Affected
- crates.io: `pancurses` — affected >=0

## Details
An issue was discovered in the pancurses crate through 0.16.1 for Rust. printw and mvprintw have format string vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15546
- https://github.com/RustSec/advisory-db/issues/106
- https://github.com/ihalila/pancurses/issues/66
- https://github.com/ihalila/pancurses
- https://rustsec.org/advisories/RUSTSEC-2019-0005.html
