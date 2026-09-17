# [C] webbrowser-rs allows attackers to access arbitrary files via supplying a crafted URL

## Summary
Severity: Critical
Advisory: GHSA-m589-mv4q-p7rj
CVE: CVE-2022-45299
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-13
Source: https://github.com/advisories/GHSA-m589-mv4q-p7rj
Type: github-advisory

## Affected
- crates.io: `webbrowser` — affected >=0 <0.8.3

## Details
An issue in the IpFile argument of rust-lang webbrowser-rs v0.8.2 allows attackers to access arbitrary files via supplying a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45299
- https://github.com/amodm/webbrowser-rs/commit/431b5139e274b7e456bea27e768aaa121b97be4c
- https://github.com/amodm/webbrowser-rs
- https://github.com/amodm/webbrowser-rs/releases/tag/v0.8.3
- https://github.com/offalltn/CVE-2022-45299
