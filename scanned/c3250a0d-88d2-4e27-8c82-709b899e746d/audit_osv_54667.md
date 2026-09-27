# [H] CVE-2024-25744

## Summary
Severity: High
Advisory: CVE-2024-25744
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-02-12
Source: https://osv.dev/vulnerability/CVE-2024-25744
Type: osv

## Details
In the Linux kernel before 6.6.7, an untrusted VMM can trigger int80 syscall handling at any given point. This is related to arch/x86/coco/tdx/tdx.c and arch/x86/mm/mem_encrypt_amd.c.

## References
- https://security.netapp.com/advisory/ntap-20241115-0006/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b82a8dbd3d2f4563156f7150c6f2ecab6e960b30
