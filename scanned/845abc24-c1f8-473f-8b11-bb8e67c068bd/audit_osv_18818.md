# [C] CVE-2020-36328

## Summary
Severity: Critical
Advisory: CVE-2020-36328
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-21
Source: https://osv.dev/vulnerability/CVE-2020-36328
Type: osv

## Details
A flaw was found in libwebp in versions before 1.0.1. A heap-based buffer overflow in function WebPDecodeRGBInto is possible due to an invalid check for buffer size. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- http://seclists.org/fulldisclosure/2021/Jul/54
- https://lists.debian.org/debian-lts-announce/2021/06/msg00005.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00006.html
- https://security.netapp.com/advisory/ntap-20211112-0001/
- https://support.apple.com/kb/HT212601
- https://www.debian.org/security/2021/dsa-4930
- https://bugzilla.redhat.com/show_bug.cgi?id=1956829
