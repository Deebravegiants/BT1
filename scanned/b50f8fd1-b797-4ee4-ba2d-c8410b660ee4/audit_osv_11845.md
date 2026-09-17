# [H] CVE-2018-0493

## Summary
Severity: High
Advisory: CVE-2018-0493
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-03
Source: https://osv.dev/vulnerability/CVE-2018-0493
Type: osv

## Details
remctld in remctl before 3.14, when an attacker is authorized to execute a command that uses the sudo option, has a use-after-free that leads to a daemon crash, memory corruption, or arbitrary command execution.

## References
- https://git.eyrie.org/?p=kerberos/remctl.git%3Ba=commit%3Bh=86c7e44090c988112a37589d2c7a94029eb5e641
- https://www.debian.org/security/2018/dsa-4159
- https://www.eyrie.org/~eagle/software/remctl/security/2018-04-01.html
