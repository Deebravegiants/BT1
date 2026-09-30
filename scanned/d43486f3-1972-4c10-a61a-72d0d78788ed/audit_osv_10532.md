# [H] CVE-2017-16875

## Summary
Severity: High
Advisory: CVE-2017-16875
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-16875
Type: osv

## Details
An issue was discovered in Teluu pjproject (pjlib and pjlib-util) in PJSIP before 2.7.1. The ioqueue component may issue a double key unregistration after an attacker initiates a socket connection with specific settings and sequences. Such double key unregistration will trigger an integer overflow, which may cause ioqueue backends to reject future key registrations.

## References
- https://trac.pjsip.org/repos/milestone/release-2.7.1
- https://trac.pjsip.org/repos/ticket/2055
- https://www.debian.org/security/2018/dsa-4170
