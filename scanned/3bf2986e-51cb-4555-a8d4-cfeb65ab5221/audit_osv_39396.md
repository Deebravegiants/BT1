# [M] Nextcloud: Information Disclosure of view filter metdata via Broken Sensitive Data Masking in ViewService

## Summary
Severity: Medium
Advisory: CVE-2026-45544
Aliases: GHSA-vvxm-6jjp-m9mp
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45544
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From version 0.8.0 to before version 1.0.4, the view filter criteria is exposed to users with read-only permissions in Nextcloud Tables. This issue has been patched in versions 1.0.4 and 2.0.0.

## References
- https://hackerone.com/reports/3483753
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45544.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vvxm-6jjp-m9mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45544
- https://github.com/nextcloud/tables/pull/2312
