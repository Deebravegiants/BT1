# [C] Unrestricted Upload of File with Dangerous Type in Payload

## Summary
Severity: Critical
Advisory: GHSA-w8xh-93qh-35vw
CVE: CVE-2022-27952
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-w8xh-93qh-35vw
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <0.15.1

## Details
An arbitrary file upload vulnerability in the file upload module of PayloadCMS v0.15.0 allows attackers to execute arbitrary code via a crafted SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27952
- https://github.com/payloadcms/payload
- https://www.youtube.com/watch?v=6CfhAxA3xdQ
