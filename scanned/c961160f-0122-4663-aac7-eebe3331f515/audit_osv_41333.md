# [M] Authenticated Path Traversal in AIL Framework PDF Object Handling Enables Potential Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-59510
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N/U:Clear)
Published: 2026-07-05
Source: https://osv.dev/vulnerability/CVE-2026-59510
Type: osv

## Details
AIL Framework contains a path traversal vulnerability in its PDF object handling. Prior to commit 14c618fce4d1df02358717c48ea903706abecdf2, the PDF.get_filepath() function constructed a file path by joining the configured PDF storage directory with a path derived from a PDF object identifier, without verifying that the resolved path remained within the intended PDF_FOLDER directory.

An authenticated attacker able to invoke PDF object operations with a crafted identifier could use relative traversal sequences or absolute path components to cause AIL Framework to open files located outside the PDF storage directory. This could allow disclosure of files readable by the AIL process, including application configuration, credentials, or other sensitive local data. This vulnerability is potential due to additional errors before being able to be executed.

The fix canonicalises the resulting path with os.path.realpath() and rejects paths whose common directory is outside the configured PDF directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59510.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59510
- https://github.com/ail-project/ail-framework/commit/14c618fce4d1df02358717c48ea903706abecdf2.patch
- https://github.com/ail-project/ail-framework0
