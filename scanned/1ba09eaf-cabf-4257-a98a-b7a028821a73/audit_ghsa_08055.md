# [H] Mautic is Vulnerable to SQL Injection through Contact Activity API Sorting

## Summary
Severity: High
Advisory: GHSA-r5j5-q42h-fc93
CVE: CVE-2026-3105
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-r5j5-q42h-fc93
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=2.10.0 <5.2.10
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.8
- Packagist: `mautic/core` — affected >=7.0.0-alpha <7.0.1

## Details
### Summary
This advisory addresses a SQL Injection vulnerability in the API endpoint used for retrieving contact activities. A vulnerability exists in the query construction for the Contact Activity timeline where the parameter responsible for determining the sort direction was not strictly validated against an allowlist, potentially allowing authenticated users to inject arbitrary SQL commands via the API.

### Mitigation

Please update to **5.2.10**, **6.0.8**, **7.0.1** or later.

### Workarounds

None.

### References

If there are any questions or comments about this advisory:

Email Mautic at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-r5j5-q42h-fc93
- https://nvd.nist.gov/vuln/detail/CVE-2026-3105
- https://github.com/mautic/mautic
- https://github.com/mautic/mautic/releases/tag/5.2.10
- https://github.com/mautic/mautic/releases/tag/6.0.8
- https://github.com/mautic/mautic/releases/tag/7.0.1
