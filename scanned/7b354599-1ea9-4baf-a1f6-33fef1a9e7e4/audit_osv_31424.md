# [H] Symlink Following in txtai leads to arbitrary file write when loading untrusted embedding indices

## Summary
Severity: High
Advisory: CVE-2025-10854
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-10854
Type: osv

## Details
The txtai framework allows the loading of compressed tar files as embedding indices. While the validate function is intended to prevent path traversal vulnerabilities by ensuring safe filenames, it does not account for symbolic links within the tar file. An attacker is able to write a file anywhere in the filesystem when txtai is used to load untrusted embedding indices

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10854.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10854
- https://research.jfrog.com/vulnerabilities/txtai-arbitrary-file-write-jfsa-2025-001471363/
- https://github.com/neuml/txtai/issues/965
- https://pypi.org/project/pip
