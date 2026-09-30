# [M] CVE-2026-30452

## Summary
Severity: Medium
Advisory: CVE-2026-30452
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-30452
Type: osv

## Details
Textpattern CMS 4.9.0 contains a Broken Access Control vulnerability in the article management system that allows authenticated users with low privileges to modify articles owned by users with higher privileges. By manipulating the article ID parameter during the duplicate-and-save workflow in textpattern/include/txp_article.php, an attacker can bypass authorization checks and overwrite content belonging to other users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30452
- https://github.com/textpattern/textpattern
- https://textpattern.com/weblog/textpattern-491-released-security-fixes-patches-and-tweaks
