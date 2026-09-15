# [H] haxtheweb/haxcms-php uses insecure method for generating salt

## Summary
Severity: High
Advisory: CVE-2026-46493
Aliases: GHSA-xg43-xm47-74cp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-46493
Type: osv

## Details
HAX CMS helps manage microsite universe with PHP or NodeJs backends. Versions prior to 26.0.1 use `uniqid` for generating salts, which is unsuitable. Version 26.0.1 fixes the issue.

## References
- https://github.com/haxtheweb/haxcms-php/blob/8b8845b16e521a326929471e16903f60c6638e8f/install.php#L188-L191
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46493.json
- https://github.com/haxtheweb/issues/security/advisories/GHSA-xg43-xm47-74cp
- https://nvd.nist.gov/vuln/detail/CVE-2026-46493
- https://github.com/haxtheweb/haxcms-php/commit/4b83cbdf8782c75bdcdd4f57ba72fba1c6dac147
