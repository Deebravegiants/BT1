# [H] CVE-2020-10589

## Summary
Severity: High
Advisory: CVE-2020-10589
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-15
Source: https://osv.dev/vulnerability/CVE-2020-10589
Type: osv

## Details
v2rayL 2.1.3 allows local users to achieve root access because /etc/v2rayL/config.json is owned by a low-privileged user but contains commands that are executed as root, after v2rayL.service is restarted via Sudo.

## References
- https://gist.github.com/bash-c/6ac238e8b15e60c9105e8cb6b42ec43c#file-v2rayl-lpe-exp2-sh
