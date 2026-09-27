# [C] Vim: Arbitrary Code Execution via Python Omni-Completion

## Summary
Severity: Critical
Advisory: CVE-2026-52858
Aliases: GHSA-52mc-rq6p-rc7c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-52858
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0561, the Python omni-completion script in python3complete.vim for Vim with the +python3 interpreter enabled (and the legacy pythoncomplete.vim for builds with the +python interpreter) executes the import and from statements found in the current buffer through Python's import machinery. Because the buffer's working directory is on sys.path, opening a hostile .py file with a sibling Python package and invoking omni-completion runs that package's top-level code as the editing user. This issue has been patched in version 9.2.0561.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0561
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52858.json
- https://github.com/vim/vim/security/advisories/GHSA-52mc-rq6p-rc7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-52858
- https://github.com/vim/vim/commit/4b850457e12e1a678dd209f2868154f7553cbf8d
