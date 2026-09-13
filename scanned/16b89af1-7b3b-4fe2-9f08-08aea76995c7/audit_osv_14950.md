# [C] CVE-2019-12526

## Summary
Severity: Critical
Advisory: CVE-2019-12526
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-12526
Type: osv

## Details
An issue was discovered in Squid before 4.9. URN response handling in Squid suffers from a heap-based buffer overflow. When receiving data from a remote server in response to an URN request, Squid fails to ensure that the response can fit within the buffer. This leads to attacker controlled data overflowing in the heap.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTM74TU2BSLT5B3H4F3UDW53672NVLMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEMOYTMCCFWK5NOXSXEIH5D2VGWVXR67/
- http://www.squid-cache.org/Advisories/SQUID-2019_7.txt
- https://lists.debian.org/debian-lts-announce/2019/12/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://security.gentoo.org/glsa/202003-34
- https://usn.ubuntu.com/4213-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1156326
