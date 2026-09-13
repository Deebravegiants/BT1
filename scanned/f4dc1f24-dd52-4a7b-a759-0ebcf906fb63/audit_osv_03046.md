# [C] ALPINE-CVE-2024-32002

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-32002
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-32002
Type: osv

## Affected
- Alpine:v3.17: `git` — affected >=2.40.0 <2.39.5-r0
- Alpine:v3.18: `git` — affected >=2.40.0 <2.40.3-r0
- Alpine:v3.19: `git` — affected >=2.40.0 <2.43.4-r0
- Alpine:v3.20: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.21: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.22: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.23: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.24: `git` — affected >=2.40.0 <2.45.1-r0

## Details
Git is a revision control system. Prior to versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4, repositories with submodules can be crafted in a way that exploits a bug in Git whereby it can be fooled into writing files not into the submodule's worktree but into a `.git/` directory. This allows writing a hook that will be executed while the clone operation is still running, giving the user no opportunity to inspect the code that is being executed. The problem has been patched in versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4. If symbolic link support is disabled in Git (e.g. via `git config --global core.symlinks false`), the described attack won't work. As always, it is best to avoid cloning repositories from untrusted sources.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-32002
