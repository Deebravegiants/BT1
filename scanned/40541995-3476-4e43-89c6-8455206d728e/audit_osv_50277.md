# [H] CVE-2020-10713

## Summary
Severity: High
Advisory: CVE-2020-10713
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-10713
Type: osv

## Details
A flaw was found in grub2, prior to version 2.06. An attacker may use the GRUB 2 flaw to hijack and tamper the GRUB verification process. This flaw also allows the bypass of Secure Boot protections. In order to load an untrusted or modified kernel, an attacker would first need to establish access to the system such as gaining physical access, obtain the ability to alter a pxe-boot network, or have remote access to a networked system with root access. With this access, an attacker could then craft a string to cause a buffer overflow by injecting a malicious payload that leads to arbitrary code execution within GRUB. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://cve.openeuler.org/#/CVEInfo/CVE-2020-10713
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-grub2-code-exec-xLePCAPY
- https://usn.ubuntu.com/4432-1/
- https://security.netapp.com/advisory/ntap-20200731-0008/
- https://www.debian.org/security/2020/dsa-4735
- https://www.kb.cert.org/vuls/id/174059
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- https://eclypsium.com/2020/07/29/theres-a-hole-in-the-boot/
- https://kb.vmware.com/s/article/80181
- https://security.gentoo.org/glsa/202104-05
- https://bugzilla.redhat.com/show_bug.cgi?id=1825243
