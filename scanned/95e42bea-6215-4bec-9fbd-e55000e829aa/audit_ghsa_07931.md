# [H] FUXA allows Remote Code Execution (RCE) via the project import functionality.

## Summary
Severity: High
Advisory: GHSA-5r63-q8hg-p8qx
CVE: CVE-2025-69983
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-5r63-q8hg-p8qx
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0

## Details
FUXA v1.2.7 allows Remote Code Execution (RCE) via the project import functionality. The application does not properly sanitize or sandbox user-supplied scripts within imported project files. An attacker can upload a malicious project containing system commands, leading to full system compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69983
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/blob/master/server/api/projects/index.js
