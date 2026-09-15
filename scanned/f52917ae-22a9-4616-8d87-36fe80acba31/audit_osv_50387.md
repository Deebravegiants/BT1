# [H] CVE-2020-14375

## Summary
Severity: High
Advisory: CVE-2020-14375
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-14375
Type: osv

## Details
A flaw was found in dpdk in versions before 18.11.10 and before 19.11.5. Virtio ring descriptors, and the data they describe are in a region of memory accessible by from both the virtual machine and the host. An attacker in a VM can change the contents of the memory after vhost_crypto has validated it. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://usn.ubuntu.com/4550-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00004.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1879468
- https://www.openwall.com/lists/oss-security/2020/09/28/3
- http://www.openwall.com/lists/oss-security/2021/01/04/1
- http://www.openwall.com/lists/oss-security/2021/01/04/2
- http://www.openwall.com/lists/oss-security/2021/01/04/5
