# [H] CVE-2017-16664

## Summary
Severity: High
Advisory: CVE-2017-16664
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-21
Source: https://osv.dev/vulnerability/CVE-2017-16664
Type: osv

## Details
Code injection exists in Kernel/System/Spelling.pm in Open Ticket Request System (OTRS) 5 before 5.0.24, 4 before 4.0.26, and 3.3 before 3.3.20. In the agent interface, an authenticated remote attacker can execute shell commands as the webserver user via URL manipulation.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00015.html
- https://www.debian.org/security/2017/dsa-4047
- https://www.otrs.com/security-advisory-2017-07-security-update-otrs-framework/
