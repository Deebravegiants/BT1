# [M] Vim has a heap-buffer-overflow and a segmentation fault

## Summary
Severity: Medium
Advisory: CVE-2026-28421
Aliases: GHSA-r2gw-2x48-jj5p
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28421
Type: osv

## Details
Vim is an open source, command line text editor. Versions prior to 9.2.0077 have a heap-buffer-overflow and a segmentation fault (SEGV) exist in Vim's swap file recovery logic. Both are caused by unvalidated fields read from crafted pointer blocks within a swap file. Version 9.2.0077 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/10
- https://github.com/vim/vim/releases/tag/v9.2.0077
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28421.json
- https://github.com/vim/vim/security/advisories/GHSA-r2gw-2x48-jj5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-28421
- https://github.com/vim/vim/commit/65c1a143c331c886dc28
