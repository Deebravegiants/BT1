# [M] decompress allows arbitrary hardlink creation during archive extraction

## Summary
Severity: Medium
Advisory: GHSA-jwp9-9v96-94mx
CVE: CVE-2026-39243
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-jwp9-9v96-94mx
Type: github-advisory

## Affected
- npm: `decompress` — affected >=0

## Details
decompress before 4.2.2 allows arbitrary hardlink creation during archive extraction, enabling file read disclosure and file corruption. When processing hardlink entries (type === 'link'), the x.linkname field from the archive is passed directly to fs.link() without validation (index.js line 113). An attacker can craft an archive with a hardlink entry whose linkname is an absolute path to any file on the same filesystem. This creates a hardlink inside the extraction directory that shares the same inode as the target file, enabling both reading and overwriting the original file's content. Hardlinks are limited to files on the same filesystem and cannot target directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39243
- https://github.com/kevva/decompress/issues/113
- https://github.com/kevva/decompress
- https://www.npmjs.com/package/decompress
