# [H] Remote Code Execution Vulnerability in Atril's EPUB ebook parsing

## Summary
Severity: High
Advisory: CVE-2023-52076
Aliases: GHSA-6mf6-mxpc-jc37
CVSS: 8.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2023-52076
Type: osv

## Details
Atril Document Viewer is the default document reader of the MATE desktop environment for Linux. A path traversal and arbitrary file write vulnerability exists in versions of Atril prior to 1.26.2. This vulnerability is capable of writing arbitrary files anywhere on the filesystem to which the user opening a crafted document has access. The only limitation is that this vulnerability cannot be exploited to overwrite existing files, but that doesn't stop an attacker from achieving Remote Command Execution on the target system. Version 1.26.2 of Atril contains a patch for this vulnerability.

## References
- https://github.com/mate-desktop/atril/releases/tag/v1.26.2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52076.json
- https://github.com/mate-desktop/atril/security/advisories/GHSA-6mf6-mxpc-jc37
- https://nvd.nist.gov/vuln/detail/CVE-2023-52076
- https://github.com/mate-desktop/atril/commit/e70b21c815418a1e6ebedf6d8d31b8477c03ba50
