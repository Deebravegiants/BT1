# [H] ALPINE-CVE-2023-29007

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-29007
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-29007
Type: osv

## Affected
- Alpine:v3.14: `git` — affected >=2.31.0 <2.32.7-r0
- Alpine:v3.15: `git` — affected >=2.31.0 <2.34.8-r0
- Alpine:v3.16: `git` — affected >=2.31.0 <2.36.6-r0
- Alpine:v3.17: `git` — affected >=2.31.0 <2.38.5-r0
- Alpine:v3.18: `git` — affected >=2.31.0 <2.40.1-r0
- Alpine:v3.19: `git` — affected >=2.31.0 <2.40.1-r0
- Alpine:v3.20: `git` — affected >=2.31.0 <2.40.1-r0
- Alpine:v3.21: `git` — affected >=2.31.0 <2.40.1-r0
- Alpine:v3.22: `git` — affected >=2.31.0 <2.40.1-r0
- Alpine:v3.23: `git` — affected >=2.31.0 <2.40.1-r0
- Alpine:v3.24: `git` — affected >=2.31.0 <2.40.1-r0

## Details
Git is a revision control system. Prior to versions 2.30.9, 2.31.8, 2.32.7, 2.33.8, 2.34.8, 2.35.8, 2.36.6, 2.37.7, 2.38.5, 2.39.3, and 2.40.1, a specially crafted `.gitmodules` file with submodule URLs that are longer than 1024 characters can used to exploit a bug in `config.c::git_config_copy_or_rename_section_in_file()`. This bug can be used to inject arbitrary configuration into a user's `$GIT_DIR/config` when attempting to remove the configuration section associated with that submodule. When the attacker injects configuration values which specify executables to run (such as `core.pager`, `core.editor`, `core.sshCommand`, etc.) this can lead to a remote code execution. A fix A fix is available in versions 2.30.9, 2.31.8, 2.32.7, 2.33.8, 2.34.8, 2.35.8, 2.36.6, 2.37.7, 2.38.5, 2.39.3, and 2.40.1. As a workaround, avoid running `git submodule deinit` on untrusted repositories or without prior inspection of any submodule sections in `$GIT_DIR/config`.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-29007
