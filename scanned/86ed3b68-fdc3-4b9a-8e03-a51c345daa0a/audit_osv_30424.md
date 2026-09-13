# [M] Nextcloud Server's link reference provider can be tricked into downloading bigger files than intended

## Summary
Severity: Medium
Advisory: CVE-2024-52520
Aliases: GHSA-pxqf-cfxw-mqmj
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52520
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. Due to a pre-flighted HEAD request, the link reference provider could be tricked into downloading bigger websites than intended, to find open-graph data. It is recommended that the Nextcloud Server is upgraded to 28.0.10 or 29.0.7 and Nextcloud Enterprise Server is upgraded to 27.1.11.8, 28.0.10 or 29.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52520.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-pxqf-cfxw-mqmj
- https://nvd.nist.gov/vuln/detail/CVE-2024-52520
- https://github.com/nextcloud/server/commit/873c42b0f1383d5b6f2b7a481e1d9620ed30f44a
- https://github.com/nextcloud/server/pull/47627
