# [H] FUXA contains an insecure default configuration vulnerability

## Summary
Severity: High
Advisory: GHSA-r5m2-fqcf-qrf7
CVE: CVE-2025-69970
CWE: CWE-1188, CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-r5m2-fqcf-qrf7
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0

## Details
FUXA v1.2.7 contains an insecure default configuration vulnerability in server/settings.default.js. The 'secureEnabled' flag is commented out by default, causing the application to initialize with authentication disabled. This allows unauthenticated remote attackers to access sensitive API endpoints, modify projects, and control industrial equipment immediately after installation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69970
- https://github.com/frangoteam/FUXA/blob
- https://github.com/frangoteam/FUXA/blob/master/server/settings.default.js
