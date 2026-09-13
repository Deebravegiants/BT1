# [H] Apache Answer Unrestricted Upload of File with Dangerous Type vulnerability

## Summary
Severity: High
Advisory: GHSA-rmqp-mvv2-54c6
CVE: CVE-2024-22393
CWE: CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-rmqp-mvv2-54c6
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.2.5

## Details
Unrestricted Upload of File with Dangerous Type vulnerability in Apache Answer. This issue affects Apache Answer through 1.2.1.

Pixel Flood Attack by uploading large pixel files will cause server out of memory. A logged-in user can cause such an attack by uploading an image when posting content.

Users are recommended to upgrade to version 1.2.5, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22393
- https://github.com/apache/incubator-answer
- https://lists.apache.org/thread/f58l6dr4r74hl6o71gn47kmn44vw12cv
- http://www.openwall.com/lists/oss-security/2024/02/22/1
