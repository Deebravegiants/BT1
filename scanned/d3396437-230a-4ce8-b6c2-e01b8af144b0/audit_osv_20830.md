# [H] CVE-2021-3752

## Summary
Severity: High
Advisory: CVE-2021-3752
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3752
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s Bluetooth subsystem in the way user calls connect to the socket and disconnect simultaneously due to a race condition. This flaw allows a user to crash the system or escalate their privileges. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lore.kernel.org/lkml/20211115165435.133245729%40linuxfoundation.org/
- https://security.netapp.com/advisory/ntap-20220318-0009/
- https://www.debian.org/security/2022/dsa-5096
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1999544
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.openwall.com/lists/oss-security/2021/09/15/4
