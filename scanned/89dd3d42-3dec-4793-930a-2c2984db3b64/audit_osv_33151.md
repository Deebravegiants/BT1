# [H] bnxt_en: Fix memory corruption when FW resources change during ifdown

## Summary
Severity: High
Advisory: CVE-2025-39810
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39810
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt_en: Fix memory corruption when FW resources change during ifdown

bnxt_set_dflt_rings() assumes that it is always called before any TC has
been created.  So it doesn't take bp->num_tc into account and assumes
that it is always 0 or 1.

In the FW resource or capability change scenario, the FW will return
flags in bnxt_hwrm_if_change() that will cause the driver to
reinitialize and call bnxt_cancel_reservations().  This will lead to
bnxt_init_dflt_ring_mode() calling bnxt_set_dflt_rings() and bp->num_tc
may be greater than 1.  This will cause bp->tx_ring[] to be sized too
small and cause memory corruption in bnxt_alloc_cp_rings().

Fix it by properly scaling the TX rings by bp->num_tc in the code
paths mentioned above.  Add 2 helper functions to determine
bp->tx_nr_rings and bp->tx_nr_rings_per_tc.

## References
- https://git.kernel.org/stable/c/2747328ba2714f1a7454208dbbc1dc0631990b4a
- https://git.kernel.org/stable/c/9ab6a9950f152e094395d2e3967f889857daa185
- https://git.kernel.org/stable/c/d00e98977ef519280b075d783653e2c492fffbb6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39810.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39810
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
