# [H] FUXA contains an Unrestricted File Upload vulnerability

## Summary
Severity: High
Advisory: GHSA-7g56-fwxj-cm23
CVE: CVE-2025-69981
CWE: CWE-306, CWE-434
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-7g56-fwxj-cm23
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0

## Details
FUXA v1.2.7 contains an Unrestricted File Upload vulnerability in the `/api/upload` API endpoint. The endpoint lacks authentication mechanisms, allowing unauthenticated remote attackers to upload arbitrary files. This can be exploited to overwrite critical system files (such as the SQLite user database) to gain administrative access, or to upload malicious scripts to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69981
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/blob/master/server/api/projects/index.js#L193
