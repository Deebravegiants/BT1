# [C] CVE-2020-36330

## Summary
Severity: Critical
Advisory: CVE-2020-36330
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-05-21
Source: https://osv.dev/vulnerability/CVE-2020-36330
Type: osv

## Details
A flaw was found in libwebp in versions before 1.0.1. An out-of-bounds read was found in function ChunkVerifyAndAssign. The highest threat from this vulnerability is to data confidentiality and to the service availability.

## References
- https://support.apple.com/kb/HT212601
- http://seclists.org/fulldisclosure/2021/Jul/54
- https://lists.debian.org/debian-lts-announce/2021/06/msg00005.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00006.html
- https://security.netapp.com/advisory/ntap-20211104-0004/
- https://www.debian.org/security/2021/dsa-4930
- https://bugzilla.redhat.com/show_bug.cgi?id=1956853
