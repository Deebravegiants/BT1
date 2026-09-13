# [H] HomeGallery: Path Traversal (Arbitrary File Read)

## Summary
Severity: High
Advisory: CVE-2026-28679
Aliases: GHSA-xj65-hcj5-h6j3
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28679
Type: osv

## Details
Home-Gallery.org is a self-hosted open-source web gallery to browse personal photos and videos. Prior to version 1.21.0, when a user requests a download, the application does not verify whether the requested file is located within the media source directory, which can result in sensitive system files being downloadable as well. This issue has been patched in version 1.21.0.

## References
- https://github.com/xemle/home-gallery/releases/tag/v1.21.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28679.json
- https://github.com/xemle/home-gallery/security/advisories/GHSA-xj65-hcj5-h6j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28679
