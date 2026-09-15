# [C] CVE-2024-37407

## Summary
Severity: Critical
Advisory: CVE-2024-37407
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-08
Source: https://osv.dev/vulnerability/CVE-2024-37407
Type: osv

## Details
Libarchive before 3.7.4 allows name out-of-bounds access when a ZIP archive has an empty-name file and mac-ext is enabled. This occurs in slurp_central_directory in archive_read_support_format_zip.c.

## References
- https://github.com/libarchive/libarchive/releases/tag/v3.7.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37407.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37407
- https://github.com/libarchive/libarchive/commit/b6a979481b7d77c12fa17bbed94576b63bbcb0c0
- https://github.com/libarchive/libarchive/pull/2145
