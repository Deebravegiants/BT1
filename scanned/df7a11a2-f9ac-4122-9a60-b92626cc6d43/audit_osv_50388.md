# [H] CVE-2020-14376

## Summary
Severity: High
Advisory: CVE-2020-14376
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-14376
Type: osv

## Details
A flaw was found in dpdk in versions before 18.11.10 and before 19.11.5. A lack of bounds checking when copying iv_data from the VM guest memory into host memory can lead to a large buffer overflow. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://usn.ubuntu.com/4550-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00006.html
- http://www.openwall.com/lists/oss-security/2021/01/04/2
- http://www.openwall.com/lists/oss-security/2021/01/04/5
- http://www.openwall.com/lists/oss-security/2021/01/04/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1879470
- https://www.openwall.com/lists/oss-security/2020/09/28/3
