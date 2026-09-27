# [H] ALPINE-CVE-2022-20001

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-20001
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-20001
Type: osv

## Affected
- Alpine:v3.16: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.17: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.18: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.19: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.20: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.21: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.22: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.23: `fish` — affected >=3.1.0 <3.4.0-r0
- Alpine:v3.24: `fish` — affected >=3.1.0 <3.4.0-r0

## Details
fish is a command line shell. fish version 3.1.0 through version 3.3.1 is vulnerable to arbitrary code execution. git repositories can contain per-repository configuration that change the behavior of git, including running arbitrary commands. When using the default configuration of fish, changing to a directory automatically runs `git` commands in order to display information about the current repository in the prompt. If an attacker can convince a user to change their current directory into one controlled by the attacker, such as on a shared file system or extracted archive, fish will run arbitrary commands under the attacker's control. This problem has been fixed in fish 3.4.0. Note that running git in these directories, including using the git tab completion, remains a potential trigger for this issue. As a workaround, remove the `fish_git_prompt` function from the prompt.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-20001
