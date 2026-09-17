# [M] SQL Injection in tribalsystems/zenario

## Summary
Severity: Medium
Advisory: GHSA-gxcm-36qw-j29v
CVE: CVE-2021-27672
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-gxcm-36qw-j29v
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0 <8.8.53370

## Details
SQL Injection in the "admin_boxes.ajax.php" component of Tribal Systems Zenario CMS v8.8.52729 allows remote attackers to obtain sesnitive database information by injecting SQL commands into the "cID" parameter when creating a new HTML component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27672
- https://github.com/TribalSystems/Zenario/commit/2c82a4d126c8446106347ef603b157f2d4175fd1
- https://deadsh0t.medium.com/blind-error-based-authenticated-sql-injection-on-zenario-8-8-52729-cms-d4705534df38
- https://github.com/TribalSystems/Zenario/releases/tag/8.8.53370
