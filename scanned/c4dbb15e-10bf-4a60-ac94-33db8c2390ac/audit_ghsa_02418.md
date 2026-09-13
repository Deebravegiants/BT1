# [M] Data races in concread

## Summary
Severity: Medium
Advisory: GHSA-4xj5-vv9x-63jp
CVE: CVE-2020-35928
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4xj5-vv9x-63jp
Type: github-advisory

## Affected
- crates.io: `concread` — affected >=0 <0.2.6

## Details
An issue was discovered in the concread crate before 0.2.6 for Rust. Attackers can cause an ARCache<K,V> data race by sending types that do not implement Send/Sync.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35928
- https://github.com/kanidm/concread/issues/48
- https://github.com/kanidm/concread
- https://rustsec.org/advisories/RUSTSEC-2020-0092.html
