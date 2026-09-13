# [H] CVE-2020-14377

## Summary
Severity: High
Advisory: CVE-2020-14377
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-14377
Type: osv

## Details
A flaw was found in dpdk in versions before 18.11.10 and before 19.11.5. A complete lack of validation of attacker-controlled parameters can lead to a buffer over read. The results of the over read are then written back to the guest virtual machine memory. This vulnerability can be used by an attacker in a virtual machine to read significant amounts of host memory. The highest threat from this vulnerability is to data confidentiality and system availability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00006.html
- http://www.openwall.com/lists/oss-security/2021/01/04/1
- http://www.openwall.com/lists/oss-security/2021/01/04/2
- http://www.openwall.com/lists/oss-security/2021/01/04/5
- https://usn.ubuntu.com/4550-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1879472
- https://www.openwall.com/lists/oss-security/2020/09/28/3
