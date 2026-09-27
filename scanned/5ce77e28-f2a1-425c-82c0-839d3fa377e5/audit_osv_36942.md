# [M] Unauthenticated Information Disclosure via .htaccess Reliance in Sensitive Directories

## Summary
Severity: Medium
Advisory: CVE-2026-27161
Aliases: GHSA-f63g-xh6j-q56g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-27161
Type: osv

## Details
GetSimple CMS is a content management system. All versions of GetSimple CMS rely on .htaccess files to restrict access to sensitive directories such as /data/ and /backups/. If Apache AllowOverride is disabled (common in hardened or shared hosting environments), these protections are silently ignored, allowing unauthenticated attackers to list and download sensitive files including authorization.xml, which contains cryptographic salts and API keys. This issue does not have a fix at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27161.json
- https://github.com/GetSimpleCMS-CE/GetSimpleCMS-CE/security/advisories/GHSA-f63g-xh6j-q56g
- https://nvd.nist.gov/vuln/detail/CVE-2026-27161
