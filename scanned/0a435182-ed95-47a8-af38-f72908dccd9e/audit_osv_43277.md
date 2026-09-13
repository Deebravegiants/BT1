# [C] Vim: Arbitrary Command Execution via Malicious `.VimballRecord` Entry Replay in `vimball.vim`

## Summary
Severity: Critical
Advisory: CVE-2026-73076
Aliases: GHSA-r22p-fhw4-84p2
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73076
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0847, runtime/autoload/vimball.vim allows a crafted vimball member named .VimballRecord to overwrite the installation record with attacker-chosen commands. When vimball#RmVimball() later processes the matching record entry, the stored Ex commands, including operating-system commands invoked through :!, execute with the privileges of the user running Vim. This issue is fixed in version 9.2.0847.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73076.json
- https://github.com/vim/vim/security/advisories/GHSA-r22p-fhw4-84p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73076
- https://github.com/vim/vim/commit/581a2f3ac9c6f96a26324f6b2c8c11415fd0d452
