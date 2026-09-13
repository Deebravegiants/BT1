# [M] Authentication headers exposed on by Nextcloud Server

## Summary
Severity: Medium
Advisory: CVE-2022-36074
Aliases: GHSA-vqgm-f748-g76v
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2022-09-15
Source: https://osv.dev/vulnerability/CVE-2022-36074
Type: osv

## Details
Nextcloud server is an open source personal cloud product. Affected versions of this package are vulnerable to Information Exposure which fails to strip the Authorization header on HTTP downgrade. This can lead to account access exposure and compromise. It is recommended that the Nextcloud Server is upgraded to 23.0.7 or 24.0.3. It is recommended that the Nextcloud Enterprise Server is upgraded to 22.2.11, 23.0.7 or 24.0.3. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36074.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vqgm-f748-g76v
- https://nvd.nist.gov/vuln/detail/CVE-2022-36074
- https://github.com/nextcloud/server/pull/32941
