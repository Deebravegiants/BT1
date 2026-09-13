# [M] Permissions bypass in Nextcloud with the files zip app

## Summary
Severity: Medium
Advisory: CVE-2024-22404
Aliases: GHSA-vhj3-mch4-67fq
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2024-22404
Type: osv

## Details
Nextcloud files Zip app is a tool to create zip archives from one or multiple files from within Nextcloud. In affected versions users can download "view-only" files by zipping the complete folder. It is recommended that the Files ZIP app is upgraded to 1.2.1, 1.4.1, or 1.5.0. Users unable to upgrade should disable the file zip app.

## References
- https://hackerone.com/reports/2247457
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22404.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vhj3-mch4-67fq
- https://nvd.nist.gov/vuln/detail/CVE-2024-22404
- https://github.com/nextcloud/files_zip/commit/43204539d517a13e945b90652718e2a213f46820
