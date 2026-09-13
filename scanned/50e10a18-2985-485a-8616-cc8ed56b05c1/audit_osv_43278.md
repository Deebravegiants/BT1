# [C] Vim: Arbitrary Code Execution via Shell Keyword Lookup

## Summary
Severity: Critical
Advisory: CVE-2026-73077
Aliases: GHSA-r5v6-q6j8-8qw2
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73077
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0839, the runtime/ftplugin/sh.vim, runtime/ftplugin/zsh.vim, and runtime/ftplugin/ps1.vim filetype plugins pass attacker-controlled Visual-mode selections from K through keywordprg commands without safely separating shell arguments. fnameescape() and PATH_ESC_CHARS do not neutralize shell metacharacters before ShKeywordPrg, ZshKeywordPrg, or GetHelp invokes bash, zsh, or PowerShell, allowing arbitrary operating-system commands to execute with the privileges of the user running Vim. This issue is fixed in version 9.2.0839.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73077.json
- https://github.com/vim/vim/security/advisories/GHSA-r5v6-q6j8-8qw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73077
- https://github.com/vim/vim/commit/c5a82fe013e73c98004ad7cd4f906b1ad1ed610e
