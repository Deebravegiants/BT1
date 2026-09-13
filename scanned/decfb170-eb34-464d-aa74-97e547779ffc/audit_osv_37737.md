# [M] FileRise: WebDAV upload path bypasses filename validation enforced by regular uploads

## Summary
Severity: Medium
Advisory: CVE-2026-33071
Aliases: GHSA-46gv-gf5f-wvr2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33071
Type: osv

## Details
FileRise is a self-hosted web file manager / WebDAV server. In versions prior to 3.8.0, the WebDAV upload endpoint accepts any file extension including .phtml, .php5, .htaccess, and other server-side executable types, bypassing the filename validation enforced by the regular upload path. In non-default deployments lacking Apache's LocationMatch protection, this leads to remote code execution. When files are uploaded via WebDAV, the createFile() method in FileRiseDirectory.php and the put() method in FileRiseFile.php accept the filename directly from the WebDAV client without any validation. In contrast, the regular upload endpoint in UploadModel::upload() validates filenames against REGEX_FILE_NAME. This issue is fixed in version 3.8.0.

## References
- https://github.com/error311/FileRise/releases/tag/v3.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33071.json
- https://github.com/error311/FileRise/security/advisories/GHSA-46gv-gf5f-wvr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33071
