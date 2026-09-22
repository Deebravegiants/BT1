# [C] A remote command execution (RCE) vulnerability in the /api/runscript endpoint of FUXA

## Summary
Severity: Critical
Advisory: GHSA-r87q-fq37-pvr6
CVE: CVE-2023-33831
CWE: CWE-77, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-18
Source: https://github.com/advisories/GHSA-r87q-fq37-pvr6
Type: github-advisory

## Affected
- npm: `@frangoteam/fuxa` — affected >=0

## Details
A remote command execution (RCE) vulnerability in the /api/runscript endpoint of FUXA 1.1.13 allows attackers to execute arbitrary commands via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33831
- https://github.com/frangoteam/FUXA
- https://github.com/rodolfomarianocy/Unauthenticated-RCE-FUXA-CVE-2023-33831
- https://youtu.be/Xxa6yRB2Fpw
