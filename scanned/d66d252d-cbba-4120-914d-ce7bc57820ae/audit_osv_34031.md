# [M] Vim has path traversal issue with zip.vim and special crafted zip archives

## Summary
Severity: Medium
Advisory: CVE-2025-53906
Aliases: GHSA-r2fw-9cw4-mj86
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:N/I:L/A:L)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-53906
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.1.1551, a path traversal issue in Vim’s zip.vim plugin can allow overwriting of arbitrary files when opening specially crafted zip archives. Impact is low because this exploit requires direct user interaction. However, successfully exploitation can lead to overwriting sensitive files or placing executable code in privileged locations, depending on the permissions of the process editing the archive. The victim must edit such a file using Vim which will reveal the filename and the file content, a careful user may suspect some strange things going on. Successful exploitation could results in the ability to execute arbitrary commands on the underlying operating system. Version 9.1.1551 contains a patch for the vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2025/07/15/2
- http://www.openwall.com/lists/oss-security/2026/04/01/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53906.json
- https://github.com/vim/vim/security/advisories/GHSA-r2fw-9cw4-mj86
- https://nvd.nist.gov/vuln/detail/CVE-2025-53906
- https://github.com/vim/vim/commit/586294a04179d855c3d1d4ee5ea83931963680b8
