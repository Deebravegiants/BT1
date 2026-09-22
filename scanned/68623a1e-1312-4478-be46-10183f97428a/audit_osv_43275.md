# [C] Vim: Arbitrary Ex Command Execution in C Omni-Completion

## Summary
Severity: Critical
Advisory: CVE-2026-73073
Aliases: GHSA-cx73-phcg-3j5g
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-73073
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0845, StructMembers() in runtime/autoload/ccomplete.vim constructs and executes a vimgrep command using an insufficiently escaped typeref: or typename: value from a tags file, allowing an unterminated collection followed by a command separator to execute arbitrary Ex and operating-system commands when a user invokes C omni-completion with CTRL-X CTRL-O on a member access whose type is resolved from that tags file. This issue is fixed in version 9.2.0845.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73073.json
- https://github.com/vim/vim/security/advisories/GHSA-cx73-phcg-3j5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-73073
- https://github.com/vim/vim/commit/2f628d8104958fa7421664f792ca6d4f7a39a10f
