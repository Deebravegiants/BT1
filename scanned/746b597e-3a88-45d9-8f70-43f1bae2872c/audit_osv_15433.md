# [H] CVE-2019-16201

## Summary
Severity: High
Advisory: CVE-2019-16201
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-16201
Type: osv

## Details
WEBrick::HTTPAuth::DigestAuth in Ruby through 2.4.7, 2.5.x through 2.5.6, and 2.6.x through 2.6.4 has a regular expression Denial of Service cause by looping/backtracking. A victim must expose a WEBrick server that uses DigestAuth to the Internet or a untrusted network.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00009.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00027.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://seclists.org/bugtraq/2019/Dec/31
- https://seclists.org/bugtraq/2019/Dec/32
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://hackerone.com/reports/661722
- https://lists.debian.org/debian-lts-announce/2019/11/msg00025.html
- https://security.gentoo.org/glsa/202003-06
- https://www.debian.org/security/2019/dsa-4587
