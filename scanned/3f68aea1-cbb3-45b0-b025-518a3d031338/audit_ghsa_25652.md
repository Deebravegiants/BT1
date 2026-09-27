# [H] Code Injection in Bolt CMS

## Summary
Severity: High
Advisory: GHSA-gprh-7767-cw39
CVE: CVE-2021-40219
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-gprh-7767-cw39
Type: github-advisory

## Affected
- Packagist: `bolt/core` — affected >=0

## Details
Bolt CMS <= 4.2 is vulnerable to Remote Code Execution. Unsafe theme rendering allows an authenticated attacker to edit theme to inject server-side template injection that leads to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40219
- https://github.com/bolt/core
- https://github.com/bolt/core/blob/3b21a73ebf519b76756d3ad2841312d10ef11461/src/Controller/Frontend/TemplateController.php
- https://github.com/iiSiLvEr/CVEs/tree/main/CVE-2021-40219
- http://boltcms.com
