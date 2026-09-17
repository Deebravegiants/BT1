# [M] Improper Certificate Validation in security-framework

## Summary
Severity: Medium
Advisory: GHSA-jqqr-c2r2-9cvr
CVE: CVE-2017-18588
CWE: CWE-295
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jqqr-c2r2-9cvr
Type: github-advisory

## Affected
- crates.io: `security-framework` — affected >=0 <0.1.12

## Details
If custom root certificates were registered with a ClientBuilder, the hostname of the target server would not be validated against its presented leaf certificate. This issue was fixed by properly configuring the trust evaluation logic to perform that check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18588
- https://github.com/sfackler/rust-security-framework/pull/27
- https://github.com/sfackler/rust-security-framework
- https://rustsec.org/advisories/RUSTSEC-2017-0003.html
