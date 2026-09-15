# [H] CVE-2020-14162

## Summary
Severity: High
Advisory: CVE-2020-14162
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-14162
Type: osv

## Details
An issue was discovered in Pi-Hole through 5.0. The local www-data user has sudo privileges to execute the pihole core script as root without a password, which could allow an attacker to obtain root access via shell metacharacters to this script's setdns command.

## References
- https://docs.pi-hole.net/core/pihole-command/
- https://0xpanic.github.io/2020/07/21/Pihole.html
