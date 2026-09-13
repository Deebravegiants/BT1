# [H] Nextcloud Server can reshare read&share only folder with more permissions

## Summary
Severity: High
Advisory: CVE-2024-37882
Aliases: GHSA-jjm3-j9xh-5xmq
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-06-14
Source: https://osv.dev/vulnerability/CVE-2024-37882
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. A recipient of a share with read&share permissions could reshare the item with more permissions. It is recommended that the Nextcloud Server is upgraded to 26.0.13 or 27.1.8 or 28.0.4 and that the Nextcloud Enterprise Server is upgraded to 26.0.13 or 27.1.8 or 28.0.4.

## References
- https://hackerone.com/reports/2289425
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37882.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-jjm3-j9xh-5xmq
- https://nvd.nist.gov/vuln/detail/CVE-2024-37882
- https://github.com/nextcloud/server/pull/44339
