# [M] FileBrowser before 2.63.19 Disk Exhaustion via TUS Upload

## Summary
Severity: Medium
Advisory: CVE-2026-72838
Aliases: GHSA-ffv3-7h97-993q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72838
Type: osv

## Details
FileBrowser versions before 2.63.19 fail to enforce the declared Upload-Length in the TUS resumable-upload PATCH endpoint, allowing authenticated users to write arbitrary data to disk. Attackers can send oversized request bodies that exceed the declared upload length to exhaust available disk space and cause service unavailability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72838.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-ffv3-7h97-993q
- https://nvd.nist.gov/vuln/detail/CVE-2026-72838
- https://www.vulncheck.com/advisories/filebrowser-before-disk-exhaustion-via-tus-upload
- https://github.com/filebrowser/filebrowser/commit/4daddec6f200b03a721197d8c0b4b652c994894e
