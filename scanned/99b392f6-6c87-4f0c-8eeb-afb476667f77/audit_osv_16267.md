# [H] CVE-2019-3857

## Summary
Severity: High
Advisory: CVE-2019-3857
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-3857
Type: osv

## Details
An integer overflow flaw which could lead to an out of bounds write was discovered in libssh2 before 1.8.1 in the way SSH_MSG_CHANNEL_REQUEST packets with an exit signal are parsed. A remote attacker who compromises a SSH server may be able to execute code on the client system when a user connects to the server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5DK6VO2CEUTAJFYIKWNZKEKYMYR3NO2O/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00003.html
- https://access.redhat.com/errata/RHSA-2019:0679
- https://access.redhat.com/errata/RHSA-2019:1175
- https://access.redhat.com/errata/RHSA-2019:1652
- https://access.redhat.com/errata/RHSA-2019:1791
- https://access.redhat.com/errata/RHSA-2019:1943
- https://access.redhat.com/errata/RHSA-2019:2399
- https://lists.debian.org/debian-lts-announce/2019/03/msg00032.html
- https://seclists.org/bugtraq/2019/Apr/25
- https://security.netapp.com/advisory/ntap-20190327-0005/
- https://www.debian.org/security/2019/dsa-4431
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3857
- https://www.libssh2.org/CVE-2019-3857.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
