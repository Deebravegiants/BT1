# [C] Vim: Vimscript Code Injection in netrw NetrwBookHistSave() via crafted directory name

## Summary
Severity: Critical
Advisory: CVE-2026-47162
Aliases: GHSA-crm5-rh6j-2c7c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47162
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0495, a Vimscript code injection vulnerability exists in s:NetrwBookHistSave() in the netrw plugin (runtime/pack/dist/opt/netrw/autoload/netrw.vim) when serializing browsed directory paths to the history file ~/.vim/.netrwhist. A directory name derived from the filesystem is interpolated into a single-quoted Vimscript string literal without escaping embedded single quotes, allowing a crafted directory name to break out of the string context and execute arbitrary Vimscript, including shell commands via system() and :!, the next time the history file is sourced. This issue has been patched in version 9.2.0495.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0495
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-47162.json
- https://access.redhat.com/errata/RHSA-2026:38509
- https://access.redhat.com/errata/RHSA-2026:38510
- https://access.redhat.com/errata/RHSA-2026:38511
- https://access.redhat.com/errata/RHSA-2026:53371
- https://access.redhat.com/errata/RHSA-2026:54769
- https://access.redhat.com/errata/RHSA-2026:55431
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/security/cve/CVE-2026-47162
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47162.json
- https://github.com/vim/vim/security/advisories/GHSA-crm5-rh6j-2c7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-47162
- https://bugzilla.redhat.com/show_bug.cgi?id=2487964
- https://github.com/vim/vim/commit/f08ab2f4d7d2947c8dd6c179ae08ee6146a2694b
