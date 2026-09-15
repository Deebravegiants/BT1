# [M] Grav CMS — Improper Handling of Highly Compressed Data in Installer::unZip()

## Summary
Severity: Medium
Advisory: CVE-2026-59193
Aliases: GHSA-2vcx-h8p2-9pg9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-59193
Type: osv

## Details
Grav is a file-based Web platform. Prior to 2.0.0, an authenticated admin.super user can crash Grav or fill the disk by uploading a specially crafted ZIP archive through the Direct Install tool because Installer::unZip calls ZipArchive::extractTo without limits on uncompressed size, entry count, or directory depth. This issue is fixed in version 2.0.0.

## References
- https://github.com/getgrav/grav/releases/tag/2.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59193.json
- https://github.com/getgrav/grav/security/advisories/GHSA-2vcx-h8p2-9pg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-59193
- https://github.com/getgrav/grav/commit/23d6f2adf4ce11889c088ac8557c8314baeef781
