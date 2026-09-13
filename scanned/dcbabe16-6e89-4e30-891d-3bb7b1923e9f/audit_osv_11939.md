# [C] CVE-2018-1000140

## Summary
Severity: Critical
Advisory: CVE-2018-1000140
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-23
Source: https://osv.dev/vulnerability/CVE-2018-1000140
Type: osv

## Details
rsyslog librelp version 1.2.14 and earlier contains a Buffer Overflow vulnerability in the checking of x509 certificates from a peer that can result in Remote code execution. This attack appear to be exploitable a remote attacker that can connect to rsyslog and trigger a stack buffer overflow by sending a specially crafted x509 certificate.

## References
- http://packetstormsecurity.com/files/172829/librelp-Remote-Code-Execution.html
- https://access.redhat.com/errata/RHSA-2018:1223
- https://access.redhat.com/errata/RHSA-2018:1225
- https://access.redhat.com/errata/RHSA-2018:1701
- https://access.redhat.com/errata/RHSA-2018:1702
- https://access.redhat.com/errata/RHSA-2018:1703
- https://access.redhat.com/errata/RHSA-2018:1704
- https://access.redhat.com/errata/RHSA-2018:1707
- https://security.gentoo.org/glsa/201804-21
- https://usn.ubuntu.com/3612-1/
- https://www.debian.org/security/2018/dsa-4151
- https://github.com/rsyslog/librelp/blob/532aa362f0f7a8d037505b0a27a1df452f9bac9e/src/tcp.c#L1205
- https://lgtm.com/rules/1505913226124/
