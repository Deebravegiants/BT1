# [C] libgit2 versions v0.27.0 through v1.9.0 built with the libssh2 SSH backend (USE_SSH=libssh2)...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1275
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1275
Type: osv

## Affected
- Julia: `LibGit2_jll` — affected >=0 <1.9.1+0

## Details
libgit2 versions v0.27.0 through v1.9.0 built with the libssh2 SSH backend (`USE_SSH`=libssh2) contain a shell command injection vulnerability that allows remote attackers to execute arbitrary commands on an SSH server by supplying a repository path containing unescaped shell metacharacters such as single quotes, semicolons, or pipes. The `gen_proto()` function in `ssh_libssh2.c` inserts the repository path directly into a shell command string without escaping special characters before passing it to `libssh2_channel_exec()`, enabling an attacker to craft a malicious submodule URL in a .gitmodules file that, when processed during a recursive clone, causes the remote server's shell to interpret injected commands under the victim's SSH user account.

## References
- https://github.com/advisories/GHSA-3gwr-xcwq-7892
- https://github.com/libgit2/libgit2
- https://nvd.nist.gov/vuln/detail/CVE-2026-5917
- https://www.vulncheck.com/advisories/libgit2-shell-command-injection-via-ssh-libssh2-backend
