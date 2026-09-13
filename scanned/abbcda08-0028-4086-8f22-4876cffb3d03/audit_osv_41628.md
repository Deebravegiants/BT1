# [M] CVE-2026-62642

## Summary
Severity: Medium
Advisory: CVE-2026-62642
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-62642
Type: osv

## Details
In Roundcube Webmail before 1.6.17 and 1.7.x before 1.7.2, an infinite loop was discovered in the TNEF decoder, which may lead to denial of service upon opening an email with a TNEF attachment.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.17
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.2
- https://roundcube.net/news/2026/07/05/security-updates-1.6.17-and-1.7.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62642.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62642
- https://github.com/roundcube/roundcubemail/commit/132ac8dd5a55c8466be12de1daf84355697ffa89
- https://github.com/roundcube/roundcubemail/commit/877269c79359d959a94f13c9070cab0f3389c193
- https://github.com/roundcube/roundcubemail/commit/a007321346380136b3de2bd75b486b04f63c0d38
- https://github.com/roundcube/roundcubemail/commit/fb952956c6eaf29e963f1a718d028d66e7957ce0
