# [M] CVE-2020-10756

## Summary
Severity: Medium
Advisory: CVE-2020-10756
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-10756
Type: osv

## Details
An out-of-bounds read vulnerability was found in the SLiRP networking implementation of the QEMU emulator. This flaw occurs in the icmp6_send_echoreply() routine while replying to an ICMP echo request, also known as ping. This flaw allows a malicious guest to leak the contents of the host memory, resulting in possible information disclosure. This flaw affects versions of libslirp before 4.3.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYTZ32P67PZER6P7TW6FQK3SZRKQLVEI/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00040.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00020.html
- https://security.netapp.com/advisory/ntap-20201001-0001/
- https://usn.ubuntu.com/4437-1/
- https://usn.ubuntu.com/4467-1/
- https://www.debian.org/security/2020/dsa-4728
- https://www.zerodayinitiative.com/advisories/ZDI-20-1005/
- https://bugzilla.redhat.com/show_bug.cgi?id=1835986
