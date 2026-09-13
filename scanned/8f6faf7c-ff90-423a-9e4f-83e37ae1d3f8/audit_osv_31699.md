# [M] drm/xe: Fix tlb invalidation when wedging

## Summary
Severity: Medium
Advisory: CVE-2025-21644
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21644
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Fix tlb invalidation when wedging

If GuC fails to load, the driver wedges, but in the process it tries to
do stuff that may not be initialized yet. This moves the
xe_gt_tlb_invalidation_init() to be done earlier: as its own doc says,
it's a software-only initialization and should had been named with the
_early() suffix.

Move it to be called by xe_gt_init_early(), so the locks and seqno are
initialized, avoiding a NULL ptr deref when wedging:

	xe 0000:03:00.0: [drm] *ERROR* GT0: load failed: status: Reset = 0, BootROM = 0x50, UKernel = 0x00, MIA = 0x00, Auth = 0x01
	xe 0000:03:00.0: [drm] *ERROR* GT0: firmware signature verification failed
	xe 0000:03:00.0: [drm] *ERROR* CRITICAL: Xe has declared device 0000:03:00.0 as wedged.
	...
	BUG: kernel NULL pointer dereference, address: 0000000000000000
	#PF: supervisor read access in kernel mode
	#PF: error_code(0x0000) - not-present page
	PGD 0 P4D 0
	Oops: Oops: 0000 [#1] PREEMPT SMP NOPTI
	CPU: 9 UID: 0 PID: 3908 Comm: modprobe Tainted: G     U  W          6.13.0-rc4-xe+ #3
	Tainted: [U]=USER, [W]=WARN
	Hardware name: Intel Corporation Alder Lake Client Platform/AlderLake-S ADP-S DDR5 UDIMM CRB, BIOS ADLSFWI1.R00.3275.A00.2207010640 07/01/2022
	RIP: 0010:xe_gt_tlb_invalidation_reset+0x75/0x110 [xe]

This can be easily triggered by poking the GuC binary to force a
signature failure. There will still be an extra message,

	xe 0000:03:00.0: [drm] *ERROR* GT0: GuC mmio request 0x4100: no reply 0x4100

but that's better than a NULL ptr deref.

(cherry picked from commit 5001ef3af8f2c972d6fd9c5221a8457556f8bea6)

## References
- https://git.kernel.org/stable/c/09b94ddc58c6640cbbc7775a61a5387b8be71488
- https://git.kernel.org/stable/c/9ab4981552930a9c45682d62424ba610edc3992d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21644.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21644
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
