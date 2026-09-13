# [H] CVE-2020-25595

## Summary
Severity: High
Advisory: CVE-2020-25595
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/CVE-2020-25595
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. The PCI passthrough code improperly uses register data. Code paths in Xen's MSI handling have been identified that act on unsanitized values read back from device hardware registers. While devices strictly compliant with PCI specifications shouldn't be able to affect these registers, experience shows that it's very common for devices to have out-of-spec "backdoor" operations that can affect the result of these reads. A not fully trusted guest may be able to crash Xen, leading to a Denial of Service (DoS) for the entire system. Privilege escalation and information leaks cannot be excluded. All versions of Xen supporting PCI passthrough are affected. Only x86 systems are vulnerable. Arm systems are not vulnerable. Only guests with passed through PCI devices may be able to leverage the vulnerability. Only systems passing through devices with out-of-spec ("backdoor") functionality can cause issues. Experience shows that such out-of-spec functionality is common; unless you have reason to believe that your device does not have such functionality, it's better to assume that it does.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4JRXMKEMQRQYWYEPHVBIWUEAVQ3LU4FN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DA633Y3G5KX7MKRN4PFEGM3IVTJMBEOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJZERRBJN6E6STDCHT4JHP4MI6TKBCJE/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00008.html
- https://security.gentoo.org/glsa/202011-06
- https://www.debian.org/security/2020/dsa-4769
- https://xenbits.xen.org/xsa/advisory-337.html
