# [C] libgit2 Shell Command Injection via ssh_libssh2 Backend

## Summary
Severity: Critical
Advisory: CVE-2026-5917
Aliases: GHSA-xqj4-2j5v-rr75
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-5917
Type: osv

## Details
libgit2 versions before 1.8.7 and 1.9.0 before 1.9.7 built with the libssh2 SSH backend (USE_SSH=libssh2) contain a shell command injection vulnerability that allows remote attackers to execute arbitrary commands on an SSH server by supplying a repository path containing unescaped shell metacharacters such as single quotes, semicolons, or pipes. The gen_proto() function in ssh_libssh2.c inserts the repository path directly into a shell command string without escaping special characters before passing it to libssh2_channel_exec(), enabling an attacker to craft a malicious submodule URL in a .gitmodules file that, when processed during a recursive clone, causes the remote server's shell to interpret injected commands under the victim's SSH user account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5917.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5917
- https://www.vulncheck.com/advisories/libgit2-shell-command-injection-via-ssh-libssh2-backend
- https://github.com/libgit2/libgit2/security/advisories/GHSA-xqj4-2j5v-rr75
