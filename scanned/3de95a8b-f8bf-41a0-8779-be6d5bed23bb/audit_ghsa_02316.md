# [H] Data races in hashconsing

## Summary
Severity: High
Advisory: GHSA-rw2c-c256-3r53
CVE: CVE-2020-36215
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rw2c-c256-3r53
Type: github-advisory

## Affected
- crates.io: `hashconsing` — affected >=0 <1.1.0

## Details
Affected versions of hashconsing implements Send/Sync for its HConsed type without restricting it to Sendable types and Syncable types. This allows non-Sync types such as Cell to be shared across threads leading to undefined behavior and memory corruption in concurrent programs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36215
- https://github.com/AdrienChampion/hashconsing/issues/1
- https://github.com/AdrienChampion/hashconsing
- https://rustsec.org/advisories/RUSTSEC-2020-0107.html
