# [H] Cross-Site Request Forgery in PiranhaCMS

## Summary
Severity: High
Advisory: GHSA-ppq7-88c7-q879
CVE: CVE-2021-25976
CWE: CWE-352
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-11-17
Source: https://github.com/advisories/GHSA-ppq7-88c7-q879
Type: github-advisory

## Affected
- NuGet: `Piranha` — affected >=4.0.0-alpha1 <10.0-alpha1

## Details
In PiranhaCMS, versions 4.0.0-alpha1 to 9.2.0 are vulnerable to cross-site request forgery (CSRF) when performing various actions supported by the management system, such as deleting a user, deleting a role, editing a post, deleting a media folder etc., when an ID is known.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25976
- https://github.com/PiranhaCMS/piranha.core/commit/e42abacdd0dd880ce9cf6607efcc24646ac82eda
- https://github.com/PiranhaCMS/piranha.core
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25976
