# [M] CyberPanel 2.4.3 Arbitrary File Read via File Manager ZIP Upload

## Summary
Severity: Medium
Advisory: CVE-2026-71964
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71964
Type: osv

## Details
CyberPanel 2.4.3, fixed in commit eca0c3c, contains an arbitrary file read vulnerability in the file manager component that allows authenticated attackers to read sensitive system files by uploading a crafted ZIP archive containing symbolic links. Attackers can exploit the application's failure to validate symlinks before extraction, causing symbolic links targeting arbitrary filesystem paths outside the user's home directory to persist on disk and be accessed through the web interface.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71964.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71964
- https://www.vulncheck.com/advisories/cyberpanel-arbitrary-file-read-via-file-manager-zip-upload
- https://github.com/usmannasir/cyberpanel/commit/eca0c3cbeb35af8eaae9fafb094e8ef3cd923643
- https://github.com/usmannasir/cyberpanel
- https://themcsam.github.io/posts/cyberpanel-2.4.3-vulnerabilties/
