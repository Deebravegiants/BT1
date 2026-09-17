# [H] Vim: vimscript injection via unescaped filename in netrw s:netrwmarkfile() filter() expression allows arbitrary code execution

## Summary
Severity: High
Advisory: CVE-2026-43961
Aliases: GHSA-66hr-7p6x-x5j3
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-43961
Type: osv

## Details
A flaw was found in Vim's netrw plugin. A crafted filename containing quote characters and expression fragments can break out of the quoted context during mark/unmark operations, allowing arbitrary Vimscript execution. This can be leveraged to run shell commands with the privileges of the user running Vim.

## References
- http://www.openwall.com/lists/oss-security/2026/05/14/7
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/vim/vim/
- https://access.redhat.com/security/cve/CVE-2026-43961
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43961.json
- https://github.com/vim/vim/security/advisories/GHSA-66hr-7p6x-x5j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-43961
- https://bugzilla.redhat.com/show_bug.cgi?id=2460434
