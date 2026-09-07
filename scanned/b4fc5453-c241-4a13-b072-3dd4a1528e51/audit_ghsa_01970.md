# [M] reflected XSS in tribalsystems/zenario

## Summary
Severity: Medium
Advisory: GHSA-8hcm-jj4x-4gmr
CVE: CVE-2021-27673
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-8hcm-jj4x-4gmr
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0 <8.8.53370

## Details
Reflected XSS in the "admin_boxes.ajax.php" component of Tribal Systems Zenario CMS v8.8.52729 allows remote attackers to execute arbitrary code by injecting into the "cID" parameter when creating a new HTML component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27673
- https://deadsh0t.medium.com/blind-error-based-authenticated-sql-injection-on-zenario-8-8-52729-cms-d4705534df38
- https://github.com/TribalSystems/Zenario
- https://github.com/TribalSystems/Zenario/releases/tag/8.8.53370
- http://packetstormsecurity.com/files/163083/Zenario-CMS-8.8.52729-SQL-Injection.html
