# [M] alkacon-OpenCMS vulnerable to stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-m44f-9jhg-59cr
CVE: CVE-2023-31544
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-m44f-9jhg-59cr
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <11.0.1

## Details
A stored cross-site scripting (XSS) vulnerability in alkacon-OpenCMS v11.0.0 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Title field under the Upload Image module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31544
- https://github.com/alkacon/opencms-core/issues/652
- https://github.com/alkacon/opencms-core/commit/21bfbeaf6b038e2c03bb421ce7f0933dd7a7633e
- https://github.com/alkacon/opencms-core
