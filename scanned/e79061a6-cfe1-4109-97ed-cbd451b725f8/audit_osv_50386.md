# [H] CVE-2020-14374

## Summary
Severity: High
Advisory: CVE-2020-14374
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-14374
Type: osv

## Details
A flaw was found in dpdk in versions before 18.11.10 and before 19.11.5. A flawed bounds checking in the copy_data function leads to a buffer overflow allowing an attacker in a virtual machine to write arbitrary data to any address in the vhost_crypto application. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00006.html
- http://www.openwall.com/lists/oss-security/2021/01/04/5
- https://bugzilla.redhat.com/show_bug.cgi?id=1879466
- https://www.openwall.com/lists/oss-security/2020/09/28/3
- http://www.openwall.com/lists/oss-security/2021/01/04/1
- http://www.openwall.com/lists/oss-security/2021/01/04/2
