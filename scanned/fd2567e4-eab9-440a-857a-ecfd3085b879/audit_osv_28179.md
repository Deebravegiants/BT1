# [H] ZITADEL vulnerable to improper HTML sanitization

## Summary
Severity: High
Advisory: CVE-2024-28855
Aliases: GHSA-hfrg-4jwr-jfpj, GO-2024-2655
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-28855
Type: osv

## Details
ZITADEL, open source authentication management software, uses Go templates to render the login UI. Due to a improper use of the `text/template` instead of the `html/template` package, the Login UI did not sanitize input parameters prior to versions 2.47.3, 2.46.1, 2.45.1, 2.44.3, 2.43.9, 2.42.15, and 2.41.15. An attacker could create a malicious link, where he injected code which would be rendered as part of the login screen. While it was possible to inject HTML including JavaScript, the execution of such scripts would be prevented by the Content Security Policy. Versions 2.47.3, 2.46.1, 2.45.1, 2.44.3, 2.43.9, 2.42.15, and 2.41.15 contain a patch for this issue. No known workarounds are available.

## References
- https://github.com/zitadel/zitadel/releases/tag/v2.41.15
- https://github.com/zitadel/zitadel/releases/tag/v2.42.15
- https://github.com/zitadel/zitadel/releases/tag/v2.43.9
- https://github.com/zitadel/zitadel/releases/tag/v2.44.3
- https://github.com/zitadel/zitadel/releases/tag/v2.45.1
- https://github.com/zitadel/zitadel/releases/tag/v2.46.1
- https://github.com/zitadel/zitadel/releases/tag/v2.47.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28855.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-hfrg-4jwr-jfpj
- https://nvd.nist.gov/vuln/detail/CVE-2024-28855
