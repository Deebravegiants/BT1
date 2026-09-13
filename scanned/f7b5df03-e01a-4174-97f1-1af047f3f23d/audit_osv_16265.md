# [H] CVE-2019-3855

## Summary
Severity: High
Advisory: CVE-2019-3855
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-3855
Type: osv

## Details
An integer overflow flaw which could lead to an out of bounds write was discovered in libssh2 before 1.8.1 in the way packets are read from the server. A remote attacker who compromises a SSH server may be able to execute code on the client system when a user connects to the server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5DK6VO2CEUTAJFYIKWNZKEKYMYR3NO2O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6LUNHPW64IGCASZ4JQ2J5KDXNZN53DWW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M7IF3LNHOA75O4WZWIHJLIRMA5LJUED3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XCWEA5ZCLKRDUK62QVVYMFWLWKOPX3LO/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00003.html
- http://packetstormsecurity.com/files/152136/Slackware-Security-Advisory-libssh2-Updates.html
- http://seclists.org/fulldisclosure/2019/Sep/42
- http://www.securityfocus.com/bid/107485
- https://access.redhat.com/errata/RHSA-2019:0679
- https://access.redhat.com/errata/RHSA-2019:1175
- https://access.redhat.com/errata/RHSA-2019:1652
- https://access.redhat.com/errata/RHSA-2019:1791
- https://access.redhat.com/errata/RHSA-2019:1943
- https://access.redhat.com/errata/RHSA-2019:2399
- https://lists.debian.org/debian-lts-announce/2019/03/msg00032.html
- https://seclists.org/bugtraq/2019/Apr/25
- https://seclists.org/bugtraq/2019/Mar/25
- https://seclists.org/bugtraq/2019/Sep/49
- https://security.netapp.com/advisory/ntap-20190327-0005/
