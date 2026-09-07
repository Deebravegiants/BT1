# [M] XSS issues in the management interface

## Summary
Severity: Medium
Advisory: GHSA-7qqr-3pj3-q2f5
CVE: CVE-2019-13236
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-7qqr-3pj3-q2f5
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <11.0.1

## Details
In system/workplace/ in Alkacon OpenCms 10.5.4 and 10.5.5, there are multiple Reflected and Stored XSS issues in the management interface.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13236
- https://aetsu.github.io/OpenCms
- https://github.com/alkacon/opencms-core/commits/branch_10_5_x
- https://twitter.com/aetsu/status/1152096227938459648
- http://packetstormsecurity.com/files/154283/Alkacon-OpenCMS-10.5.x-Cross-Site-Scripting.html
