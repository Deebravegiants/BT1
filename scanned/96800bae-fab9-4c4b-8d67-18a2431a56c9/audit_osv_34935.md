# [M] Nextcloud Tables app allowed users to view columns metadata information of any table

## Summary
Severity: Medium
Advisory: CVE-2025-66553
Aliases: GHSA-p53h-6294-crjw
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66553
Type: osv

## Details
Nextcloud Tables allows you to create your own tables with individual columns. Prior to 0.8.7 and 0.9.4, authenticated users were able to view meta data of columns in other tables of the Tables app by modifying the numeric ID in a request. This vulnerability is fixed in 0.8.7 and 0.9.4.

## References
- https://hackerone.com/reports/3138721
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66553.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-p53h-6294-crjw
- https://nvd.nist.gov/vuln/detail/CVE-2025-66553
- https://github.com/nextcloud/tables/commit/e975f5bfedb6922f04cdd236cde4e26067fe064e
- https://github.com/nextcloud/tables/pull/1891
