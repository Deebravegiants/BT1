# [M] CVE-2017-2596

## Summary
Severity: Medium
Advisory: CVE-2017-2596
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-2596
Type: osv

## Details
The nested_vmx_check_vmptr function in arch/x86/kvm/vmx.c in the Linux kernel through 4.9.8 improperly emulates the VMXON instruction, which allows KVM L1 guest OS users to cause a denial of service (host OS memory consumption) by leveraging the mishandling of page references.

## References
- http://www.debian.org/security/2017/dsa-3791
- http://www.securityfocus.com/bid/95878
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- http://www.openwall.com/lists/oss-security/2017/01/31/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1417812
