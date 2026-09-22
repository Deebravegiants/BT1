# [C] Prototype pollution in safe-obj

## Summary
Severity: Critical
Advisory: GHSA-wpgh-hmv4-r3v5
CVE: CVE-2021-25928
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-wpgh-hmv4-r3v5
Type: github-advisory

## Affected
- npm: `safe-obj` — affected >=1.0.0

## Details
Prototype pollution vulnerability in 'safe-obj' versions 1.0.0 through 1.0.2 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25928
- https://github.com/mantacode/safe-obj/blob/6ab63529182b6cf11704ac84f10800290afd3f9f/lib/index.js#L122
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25928
