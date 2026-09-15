# [H] CVE-2021-20181

## Summary
Severity: High
Advisory: CVE-2021-20181
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-20181
Type: osv

## Details
A race condition flaw was found in the 9pfs server implementation of QEMU up to and including 5.2.0. This flaw allows a malicious 9p client to cause a use-after-free error, potentially escalating their privileges on the system. The highest threat from this vulnerability is to confidentiality, integrity as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20210720-0009/
- https://www.zerodayinitiative.com/advisories/ZDI-21-159/
- https://bugzilla.redhat.com/show_bug.cgi?id=1927007
