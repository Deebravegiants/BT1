# [M] Statamic's sensitive configuration values are exposed to content editors via Antlers-enabled fields

## Summary
Severity: Medium
Advisory: GHSA-gcqf-5x9f-hq7f
CVE: CVE-2026-33886
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-gcqf-5x9f-hq7f
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=5.73.12 <5.73.16
- Packagist: `statamic/cms` — affected >=6.5.0 <6.7.2

## Details
### Impact
A control panel user with access to Antlers-enabled fields could access sensitive application configuration values by inserting config variables into their content.

### Patches
This has been fixed in 5.73.16 and 6.7.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-gcqf-5x9f-hq7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33886
- https://github.com/statamic/cms
