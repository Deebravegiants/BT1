# [H] CVE-2023-30179

## Summary
Severity: High
Advisory: CVE-2023-30179
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-13
Source: https://osv.dev/vulnerability/CVE-2023-30179
Type: osv

## Details
CraftCMS version 3.7.59 is vulnerable to Server-Side Template Injection (SSTI). An authenticated attacker can inject Twig Template to User Photo Location field when setting User Photo Location in User Settings, lead to Remote Code Execution. NOTE: the vendor disputes this because only Administrators can add this Twig code, and (by design) Administrators are allowed to do that by default.

## References
- https://datnlq.gitbook.io/cve/craft-cms/cve-2023-30179-server-side-template-injection
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#442---2023-03-14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30179.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30179
- https://github.com/github/advisory-database/pull/2443#issuecomment-1610040714
- https://github.com/github/advisory-database/pull/2443#issuecomment-1610634200
