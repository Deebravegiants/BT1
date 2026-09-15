# [M] Nextcloud Tables is missing an ownership check which allows moving columns into tables of other users

## Summary
Severity: Medium
Advisory: CVE-2025-66551
Aliases: GHSA-w787-vwqp-8wr7
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66551
Type: osv

## Details
Nextcloud Tables allows you to create your own tables with individual columns. Prior to 0.8.6 and 0.9.3, a malicious user was able to create their own table and then move a column to a victims table. This vulnerability is fixed in 0.8.6 and 0.9.3.

## References
- https://hackerone.com/reports/3137895
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66551.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-w787-vwqp-8wr7
- https://nvd.nist.gov/vuln/detail/CVE-2025-66551
- https://github.com/nextcloud/tables/commit/39f24a62fb41fd7a8bda65325f8bbafdc91c731c
- https://github.com/nextcloud/tables/pull/1810
