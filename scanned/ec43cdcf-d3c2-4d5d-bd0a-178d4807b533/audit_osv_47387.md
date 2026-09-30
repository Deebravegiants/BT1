# [H] CVE-2016-4480

## Summary
Severity: High
Advisory: CVE-2016-4480
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-18
Source: https://osv.dev/vulnerability/CVE-2016-4480
Type: osv

## Details
The guest_walk_tables function in arch/x86/mm/guest_walk.c in Xen 4.6.x and earlier does not properly handle the Page Size (PS) page table entry bit at the L4 and L3 page table levels, which might allow local guest OS users to gain privileges via a crafted mapping of memory.

## References
- http://www.securityfocus.com/bid/90710
- http://www.securitytracker.com/id/1035901
- http://www.debian.org/security/2016/dsa-3633
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://xenbits.xen.org/xsa/advisory-176.html
