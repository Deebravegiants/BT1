# [C] The Freeform CraftCMS plugin contains an Server-side template injection (SSTI) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9hp3-f5g8-rccg
CVE: CVE-2025-52122
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-27
Source: https://github.com/advisories/GHSA-9hp3-f5g8-rccg
Type: github-advisory

## Affected
- Packagist: `solspace/craft-freeform` — affected >=5.0.0 <5.10.16

## Details
Freeform 5.0.0 to before 5.10.16, a plugin for CraftCMS, contains an Server-side template injection (SSTI) vulnerability, resulting in arbitrary code injection for all users that have access to editing a form (submission title).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52122
- https://github.com/TimTrademark/CVE-2025-52122
- https://github.com/TimTrademark/CVE-CraftCMS-Freeform
- https://github.com/solspace/craft-freeform
