# [C] ALPINE-CVE-2018-19486

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-19486
Ecosystem: Alpine:v3.6, Alpine:v3.8
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19486
Type: osv

## Affected
- Alpine:v3.6: `git` — affected >=0 <2.13.7-r2
- Alpine:v3.8: `git` — affected >=0 <2.18.1-r1

## Details
Git before 2.19.2 on Linux and UNIX executes commands from the current working directory (as if '.' were at the end of $PATH) in certain cases involving the run_command() API and run-command.c, because there was a dangerous change from execvp to execv during 2017.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19486
