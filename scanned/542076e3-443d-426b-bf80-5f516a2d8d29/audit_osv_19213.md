# [C] CVE-2020-8794

## Summary
Severity: Critical
Advisory: CVE-2020-8794
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-25
Source: https://osv.dev/vulnerability/CVE-2020-8794
Type: osv

## Details
OpenSMTPD before 6.6.4 allows remote code execution because of an out-of-bounds read in mta_io in mta_session.c for multi-line replies. Although this vulnerability affects the client side of OpenSMTPD, it is possible to attack a server because the server code launches the client code during bounce handling.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OPH4QU4DNVHA7ACFXMYFCEP5PSXXPN4E/
- http://seclists.org/fulldisclosure/2020/Feb/32
- http://www.openwall.com/lists/oss-security/2020/03/01/1
- http://www.openwall.com/lists/oss-security/2020/03/01/2
- https://www.debian.org/security/2020/dsa-4634
- https://www.openbsd.org/security.html
- https://usn.ubuntu.com/4294-1/
- http://packetstormsecurity.com/files/156633/OpenSMTPD-Out-Of-Bounds-Read-Local-Privilege-Escalation.html
- http://www.openwall.com/lists/oss-security/2020/02/26/1
- http://www.openwall.com/lists/oss-security/2021/05/04/7
- https://www.openwall.com/lists/oss-security/2020/02/24/5
