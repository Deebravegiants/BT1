# [H] CVE-2020-10588

## Summary
Severity: High
Advisory: CVE-2020-10588
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-15
Source: https://osv.dev/vulnerability/CVE-2020-10588
Type: osv

## Details
v2rayL 2.1.3 allows local users to achieve root access because /etc/v2rayL/add.sh and /etc/v2rayL/remove.sh are owned by a low-privileged user but execute as root via Sudo.

## References
- https://gist.github.com/bash-c/6ac238e8b15e60c9105e8cb6b42ec43c#file-v2rayl-lpe-exp1-sh
