# [C] Buffer overflow and format vulnerabilities in ncurses

## Summary
Severity: Critical
Advisory: GHSA-g7r5-x7cr-vm3v
CVE: CVE-2019-15548
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g7r5-x7cr-vm3v
Type: github-advisory

## Affected
- crates.io: `ncurses` — affected >=0

## Details
ncurses exposes functions from the ncurses library which:
* Pass buffers without length to C functions that may write an arbitrary amount of data, leading to a buffer overflow. (instr, mvwinstr, etc)
* Passes rust &str to strings expecting C format arguments, allowing hostile input to execute a format string attack, which trivially allows writing arbitrary data to stack memory (functions in the printw family).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15548
- https://github.com/RustSec/advisory-db/issues/106
- https://github.com/jeaye/ncurses-rs/issues/172
- https://github.com/jeaye/ncurses-rs
- https://rustsec.org/advisories/RUSTSEC-2019-0006.html
