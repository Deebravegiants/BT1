# [H] Memory exhaustion in asn1_der

## Summary
Severity: High
Advisory: GHSA-v5r6-6r3c-wqxc
CVE: CVE-2019-15549
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-v5r6-6r3c-wqxc
Type: github-advisory

## Affected
- crates.io: `asn1_der` — affected >=0 <0.6.2

## Details
An issue was discovered in the asn1_der crate before 0.6.2 for Rust. Attackers can trigger memory exhaustion by supplying a large value in a length field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15549
- https://github.com/KizzyCode/asn1_der/issues/1
- https://github.com/KizzyCode/asn1_der
- https://rustsec.org/advisories/RUSTSEC-2019-0007.html
