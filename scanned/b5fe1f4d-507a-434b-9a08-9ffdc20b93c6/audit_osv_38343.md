# [H] CVE-2026-39246

## Summary
Severity: High
Advisory: CVE-2026-39246
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-39246
Type: osv

## Details
decompress before 4.2.2 allows arbitrary symlink creation during archive extraction. When processing symlink entries (type === 'symlink'), the x.linkname field from the archive is passed directly to fs.symlink() without validation (index.js line 121). The preventWritingThroughSymlink check on line 98 only applies to file entries, not symlink creation. An attacker can craft an archive with symlink entries pointing to sensitive files outside the extraction directory (e.g., /etc/passwd), enabling information disclosure when the application reads the extracted contents.

## References
- https://www.npmjs.com/package/decompress
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39246.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39246
- https://github.com/kevva/decompress/issues/114
- https://github.com/kevva/decompress
