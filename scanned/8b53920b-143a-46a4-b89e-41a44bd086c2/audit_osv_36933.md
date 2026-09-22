# [M] bit7z has a path traversal vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-27117
Aliases: GHSA-qvjh-hhw4-3gx9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-27117
Type: osv

## Details
bit7z is a cross-platform C++ static library that allows the compression/extraction of archive files. Prior to version 4.0.11, a path traversal vulnerability ("Zip Slip") exists in bit7z's archive extraction functionality. The library does not adequately validate file paths contained in archive entries, allowing files to be written outside the intended extraction directory through three distinct mechanisms: relative path traversal, absolute path traversal, and symbolic link traversal. An attacker can exploit this by providing a malicious archive to any application that uses bit7z to extract untrusted archives. Successful exploitation results in arbitrary file write with the privileges of the process performing the extraction. This could lead to overwriting of application binaries, configuration files, or other sensitive data. The vulnerability does not directly enable reading of file contents; the confidentiality impact is limited to the calling application's own behavior after extraction. However, applications that subsequently serve or display extracted files may face secondary confidentiality risks from attacker-created symlinks. Fixes have been released in version 4.0.11. If upgrading is not immediately possible, users can mitigate the vulnerability by validating each entry's destination path before writing. Other mitigations include running extraction with least privilege and extracting untrusted archives in a sandboxed directory.

## References
- https://github.com/rikyoz/bit7z/releases/tag/v4.0.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27117.json
- https://github.com/rikyoz/bit7z/security/advisories/GHSA-qvjh-hhw4-3gx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27117
- https://github.com/rikyoz/bit7z/commit/31763da9a3e41a199c141c8d71f6c11de24b45cf
- https://github.com/rikyoz/bit7z/commit/9e020483eefa5825ec9310b1d869933d4f77f969
