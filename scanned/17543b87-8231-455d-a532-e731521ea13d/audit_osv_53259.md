# [M] CVE-2022-35230

## Summary
Severity: Medium
Advisory: CVE-2022-35230
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2022-35230
Type: osv

## Details
An authenticated user can create a link with reflected Javascript code inside it for the graphs page and send it to other users. The payload can be executed only with a known CSRF token value of the victim, which is changed periodically and is difficult to predict.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00013.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://support.zabbix.com/browse/ZBX-21305
