# [H] Improper Input Validation (RCE)

## Summary
Severity: High
Advisory: GHSA-w36g-q975-37rg
CVE: CVE-2021-26814
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-w36g-q975-37rg
Type: github-advisory

## Affected
- npm: `wazuh` — affected >=4.0.0 <4.0.4

## Details
Wazuh API in Wazuh from 4.0.0 to 4.0.3 allows authenticated users to execute arbitrary code with administrative privileges via /manager/files URI. An authenticated user to the service may exploit incomplete input validation on the /manager/files API to inject arbitrary code within the API service script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26814
- https://documentation.wazuh.com/4.0/release-notes/release_4_0_4.html
- https://github.com/wazuh/wazuh/releases/tag/v4.0.4
