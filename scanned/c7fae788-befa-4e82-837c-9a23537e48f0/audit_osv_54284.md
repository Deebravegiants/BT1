# [M] CVE-2023-4611

## Summary
Severity: Medium
Advisory: CVE-2023-4611
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-08-29
Source: https://osv.dev/vulnerability/CVE-2023-4611
Type: osv

## Details
A use-after-free flaw was found in mm/mempolicy.c in the memory management subsystem in the Linux Kernel. This issue is caused by a race between mbind() and VMA-locked page fault, and may allow a local attacker to crash the system or lead to a kernel information leak.

## References
- https://access.redhat.com/security/cve/CVE-2023-4611
- https://bugzilla.redhat.com/show_bug.cgi?id=2227244
- https://www.spinics.net/lists/stable-commits/msg310136.html
