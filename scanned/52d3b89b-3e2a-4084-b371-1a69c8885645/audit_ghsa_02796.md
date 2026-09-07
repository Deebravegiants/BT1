# [C] Prototype pollution in object-hierarchy-access

## Summary
Severity: Critical
Advisory: GHSA-fxwf-45c7-4ppr
CVE: CVE-2020-28270
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-fxwf-45c7-4ppr
Type: github-advisory

## Affected
- npm: `object-hierarchy-access` — affected >=0.2.0 <0.33.0

## Details
Overview:Prototype pollution vulnerability in ‘object-hierarchy-access’ versions 0.2.0 through 0.32.0 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28270
- https://github.com/mjpclab/object-hierarchy-access/commit/7b1aa134a8bc4a376296bcfac5c3463aef2b7572
- https://github.com/mjpclab/object-hierarchy-access
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28270
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28270,
