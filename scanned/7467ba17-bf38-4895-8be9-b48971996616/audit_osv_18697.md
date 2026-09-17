# [M] CVE-2020-35505

## Summary
Severity: Medium
Advisory: CVE-2020-35505
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2020-35505
Type: osv

## Details
A NULL pointer dereference flaw was found in the am53c974 SCSI host bus adapter emulation of QEMU in versions before 6.0.0. This issue occurs while handling the 'Information Transfer' command. This flaw allows a privileged guest user to crash the QEMU process on the host, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- http://www.openwall.com/lists/oss-security/2021/04/16/3
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210713-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1909769
- https://www.openwall.com/lists/oss-security/2021/04/16/3
