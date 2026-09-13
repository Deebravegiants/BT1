# [H] CVE-2017-12154

## Summary
Severity: High
Advisory: CVE-2017-12154
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-09-26
Source: https://osv.dev/vulnerability/CVE-2017-12154
Type: osv

## Details
The prepare_vmcs02 function in arch/x86/kvm/vmx.c in the Linux kernel through 4.13.3 does not ensure that the "CR8-load exiting" and "CR8-store exiting" L0 vmcs02 controls exist in cases where L1 omits the "use TPR shadow" vmcs12 control, which allows KVM L2 guest OS users to obtain read and write access to the hardware CR8 register.

## References
- https://usn.ubuntu.com/3698-1/
- https://usn.ubuntu.com/3698-2/
- http://www.securityfocus.com/bid/100856
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2019:1946
- http://www.debian.org/security/2017/dsa-3981
- https://access.redhat.com/errata/RHSA-2018:1062
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=51aa68e7d57e3217192d88ce90fd5b8ef29ec94f
- https://bugzilla.redhat.com/show_bug.cgi?id=1491224
- https://www.spinics.net/lists/kvm/msg155414.html
- https://github.com/torvalds/linux/commit/51aa68e7d57e3217192d88ce90fd5b8ef29ec94f
