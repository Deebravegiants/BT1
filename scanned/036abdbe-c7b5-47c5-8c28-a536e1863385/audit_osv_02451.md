# [H] ALPINE-CVE-2022-24765

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24765
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24765
Type: osv

## Affected
- Alpine:v3.13: `git` — affected >=0 <2.30.3-r0
- Alpine:v3.14: `git` — affected >=0 <2.32.1-r0
- Alpine:v3.15: `git` — affected >=0 <2.34.2-r0
- Alpine:v3.16: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.17: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.18: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.19: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.20: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.21: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.22: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.23: `git` — affected >=0 <2.35.2-r0
- Alpine:v3.24: `git` — affected >=0 <2.35.2-r0

## Details
Git for Windows is a fork of Git containing Windows-specific patches. This vulnerability affects users working on multi-user machines, where untrusted parties have write access to the same hard disk. Those untrusted parties could create the folder `C:\.git`, which would be picked up by Git operations run supposedly outside a repository while searching for a Git directory. Git would then respect any config in said Git directory. Git Bash users who set `GIT_PS1_SHOWDIRTYSTATE` are vulnerable as well. Users who installed posh-gitare vulnerable simply by starting a PowerShell. Users of IDEs such as Visual Studio are vulnerable: simply creating a new project would already read and respect the config specified in `C:\.git\config`. Users of the Microsoft fork of Git are vulnerable simply by starting a Git Bash. The problem has been patched in Git for Windows v2.35.2. Users unable to upgrade may create the folder `.git` on all drives where Git commands are run, and remove read/write access from those folders as a workaround. Alternatively, define or extend `GIT_CEILING_DIRECTORIES` to cover the _parent_ directory of the user profile, e.g. `C:\Users` if the user profile is located in `C:\Users\my-user-name`.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24765
