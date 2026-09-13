# [H] CVE-2017-12188

## Summary
Severity: High
Advisory: CVE-2017-12188
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/CVE-2017-12188
Type: osv

## Details
arch/x86/kvm/mmu.c in the Linux kernel through 4.13.5, when nested virtualisation is used, does not properly traverse guest pagetable entries to resolve a guest virtual address, which allows L1 guest OS users to execute arbitrary code on the host OS or cause a denial of service (incorrect index during page walking, and host OS crash), aka an "MMU potential stack buffer overrun."

## References
- http://www.securityfocus.com/bid/101267
- https://access.redhat.com/errata/RHSA-2018:0395
- https://access.redhat.com/errata/RHSA-2018:0412
- https://bugzilla.redhat.com/show_bug.cgi?id=1500380
- https://patchwork.kernel.org/patch/9996579/
- https://patchwork.kernel.org/patch/9996587/
