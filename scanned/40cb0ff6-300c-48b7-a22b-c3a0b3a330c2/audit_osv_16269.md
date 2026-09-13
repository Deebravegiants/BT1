# [C] CVE-2019-3859

## Summary
Severity: Critical
Advisory: CVE-2019-3859
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-3859
Type: osv

## Details
An out of bounds read flaw was discovered in libssh2 before 1.8.1 in the _libssh2_packet_require and _libssh2_packet_requirev functions. A remote attacker who compromises a SSH server may be able to cause a Denial of Service or read data in the client memory.

## References
- https://lists.debian.org/debian-lts-announce/2019/07/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5DK6VO2CEUTAJFYIKWNZKEKYMYR3NO2O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XCWEA5ZCLKRDUK62QVVYMFWLWKOPX3LO/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00102.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00103.html
- http://www.securityfocus.com/bid/107485
- https://lists.debian.org/debian-lts-announce/2019/03/msg00032.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00006.html
- https://seclists.org/bugtraq/2019/Apr/25
- https://security.netapp.com/advisory/ntap-20190327-0005/
- https://www.broadcom.com/support/fibre-channel-networking/security-advisories/brocade-security-advisory-2019-767
- https://www.debian.org/security/2019/dsa-4431
- https://www.libssh2.org/CVE-2019-3859.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://packetstormsecurity.com/files/152136/Slackware-Security-Advisory-libssh2-Updates.html
- http://www.openwall.com/lists/oss-security/2019/03/18/3
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3859
- https://seclists.org/bugtraq/2019/Mar/25
