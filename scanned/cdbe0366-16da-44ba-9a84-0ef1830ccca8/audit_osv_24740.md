# [M] Nextcloud download permissions can be changed by resharer

## Summary
Severity: Medium
Advisory: CVE-2023-25821
Aliases: GHSA-7w6h-5qgw-4j94
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-02-24
Source: https://osv.dev/vulnerability/CVE-2023-25821
Type: osv

## Details
Nextcloud is an Open Source private cloud software. Versions 24.0.4 and above, prior to 24.0.7, and 25.0.0 and above, prior to 25.0.1, contain Improper Access Control. Secure view for internal shares can be circumvented if reshare permissions are also given. This issue is patched in versions 24.0.7 and 25.0.1. No workaround  is available.

## References
- https://hackerone.com/reports/1724016
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25821.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-7w6h-5qgw-4j94
- https://nvd.nist.gov/vuln/detail/CVE-2023-25821
- https://github.com/nextcloud/server/pull/34502
