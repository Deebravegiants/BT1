# [C] CVE-2018-5704

## Summary
Severity: Critical
Advisory: CVE-2018-5704
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5704
Type: osv

## Details
Open On-Chip Debugger (OpenOCD) 0.10.0 does not block attempts to use HTTP POST for sending data to 127.0.0.1 port 4444, which allows remote attackers to conduct cross-protocol scripting attacks, and consequently execute arbitrary commands, via a crafted web site.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00027.html
- https://www.debian.org/security/2018/dsa-4093
- https://sourceforge.net/p/openocd/mailman/message/36188041/
