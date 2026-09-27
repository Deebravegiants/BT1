# [C] CVE-2019-3860

## Summary
Severity: Critical
Advisory: CVE-2019-3860
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-3860
Type: osv

## Details
An out of bounds read flaw was discovered in libssh2 before 1.8.1 in the way SFTP packets with empty payloads are parsed. A remote attacker who compromises a SSH server may be able to cause a Denial of Service or read data in the client memory.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00072.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5DK6VO2CEUTAJFYIKWNZKEKYMYR3NO2O/
- https://seclists.org/bugtraq/2019/Apr/25
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00003.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00032.html
- https://security.netapp.com/advisory/ntap-20190327-0005/
- https://www.debian.org/security/2019/dsa-4431
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3860
- https://www.libssh2.org/CVE-2019-3860.html
