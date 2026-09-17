# [M] CVE-2019-14907

## Summary
Severity: Medium
Advisory: CVE-2019-14907
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2019-14907
Type: osv

## Details
All samba versions 4.9.x before 4.9.18, 4.10.x before 4.10.12 and 4.11.x before 4.11.5 have an issue where if it is set with "log level = 3" (or above) then the string obtained from the client, after a failed character conversion, is printed. Such strings can be provided during the NTLMSSP authentication exchange. In the Samba AD DC in particular, this may cause a long-lived process(such as the RPC server) to terminate. (In the file server case, the most likely target, smbd, operates as process-per-client and so a crash there is harmless).

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ACZVNMIFQGGXNJPMHAVBN3H2U65FXQY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GQ6U65I2K23YJC4FESW477WL55TU3PPT/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00055.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00023.html
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20200122-0001/
- https://usn.ubuntu.com/4244-1/
- https://www.samba.org/samba/security/CVE-2019-14907.html
- https://www.synology.com/security/advisory/Synology_SA_20_01
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14907
