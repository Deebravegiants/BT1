# [H] Remote code execution in better-macro

## Summary
Severity: High
Advisory: GHSA-79wf-qcqv-r22r
CVE: CVE-2021-38196
CWE: CWE-78, CWE-94
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-79wf-qcqv-r22r
Type: github-advisory

## Affected
- crates.io: `better-macro` — affected >=0

## Details
An issue was discovered in the better-macro crate through 2021-07-22 for Rust. It intentionally demonstrates that remote attackers can execute arbitrary code via proc-macros, and otherwise has no legitimate purpose.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38196
- https://github.com/raycar5/better-macro
- https://github.com/raycar5/better-macro/blob/24ff1702397b9c19bbfa4c660e2316cd77d3b900/src/lib.rs#L36-L38
- https://rustsec.org/advisories/RUSTSEC-2021-0077.html
