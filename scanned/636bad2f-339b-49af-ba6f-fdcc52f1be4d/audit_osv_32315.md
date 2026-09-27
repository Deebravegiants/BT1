# [H] Improper Input Validation in Vim

## Summary
Severity: High
Advisory: CVE-2025-27423
Aliases: GHSA-wfmf-8626-q3r3
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-27423
Type: osv

## Details
Vim is an open source, command line text editor. Vim is distributed with the tar.vim plugin, that allows easy editing and viewing of (compressed or uncompressed) tar files. Starting with 9.1.0858, the tar.vim plugin uses the ":read" ex command line to append below the cursor position, however the is not sanitized and is taken literally from the tar archive. This allows to execute shell commands via special crafted tar archives. Whether this really happens, depends on the shell being used ('shell' option, which is set using $SHELL). The issue has been fixed as of Vim patch v9.1.1164

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27423.json
- https://github.com/vim/vim/security/advisories/GHSA-wfmf-8626-q3r3
- https://nvd.nist.gov/vuln/detail/CVE-2025-27423
- https://security.netapp.com/advisory/ntap-20250502-0002/
- https://github.com/vim/vim/commit/129a8446d23cd9cb4445fcfea259cba5e0487d29
- https://github.com/vim/vim/commit/334a13bff78aa0ad206bc436885f63e3a0bab399
