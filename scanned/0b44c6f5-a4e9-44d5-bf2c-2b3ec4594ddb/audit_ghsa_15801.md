# [M] Apache CXF Denial of Service vulnerability in JOSE

## Summary
Severity: Medium
Advisory: GHSA-6pff-fmh2-4mmf
CVE: CVE-2024-32007
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-6pff-fmh2-4mmf
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-jose` — affected >=4.0.0 <4.0.5
- Maven: `org.apache.cxf:cxf-rt-rs-security-jose` — affected >=3.6.0 <3.6.4
- Maven: `org.apache.cxf:cxf-rt-rs-security-jose` — affected >=0 <3.5.9

## Details
An improper input validation of the p2c parameter in the Apache CXF JOSE code before 4.0.5, 3.6.4 and 3.5.9 allows an attacker to perform a denial of service attack by specifying a large value for this parameter in a token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-32007
- https://github.com/apache/cxf/commit/20793d3fed2e73e2785a58ec5b47403306ae4a5c
- https://github.com/apache/cxf/commit/2d2baa3455db7439bf1ed4e00edfc5a7106edf7d
- https://github.com/apache/cxf/commit/d1d77c34c199c2c87ebcfe23e3c81dccfe2e2473
- https://github.com/apache/cxf
- https://lists.apache.org/thread/stwrgsr1llb73nkl16klv9vjqgmmx633
