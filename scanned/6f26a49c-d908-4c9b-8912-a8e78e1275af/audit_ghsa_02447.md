# [C] Out of bounds write in calamine

## Summary
Severity: Critical
Advisory: GHSA-ppqp-78xx-3r38
CVE: CVE-2021-26951
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-ppqp-78xx-3r38
Type: github-advisory

## Affected
- crates.io: `calamine` — affected >=0 <0.17.0

## Details
An issue was discovered in the calamine crate before 0.17.0 for Rust. It allows attackers to overwrite heap-memory locations because Vec::set_len is used without proper memory claiming, and this uninitialized memory is used for a user-provided Read operation, as demonstrated by Sectors::get.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26951
- https://github.com/tafia/calamine/issues/199
- https://github.com/tafia/calamine
- https://rustsec.org/advisories/RUSTSEC-2021-0015.html
