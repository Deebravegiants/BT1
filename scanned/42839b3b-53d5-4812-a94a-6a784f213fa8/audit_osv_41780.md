# [H] drm/gpusvm: Fix unbalanced unlock in drm_gpusvm_scan_mm()

## Summary
Severity: High
Advisory: CVE-2026-63863
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63863
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/gpusvm: Fix unbalanced unlock in drm_gpusvm_scan_mm()

There is a unbalanced lock/unlock to gpusvm notifier lock:
[  931.045868] =====================================
[  931.046509] WARNING: bad unlock balance detected!
[  931.047149] 6.19.0-rc6+xe-**************** #9 Tainted: G     U
[  931.048150] -------------------------------------
[  931.048790] kworker/u5:0/51 is trying to release lock (&gpusvm->notifier_lock) at:
[  931.049801] [<ffffffffa090c0d8>] drm_gpusvm_scan_mm+0x188/0x460 [drm_gpusvm_helper]
[  931.050802] but there are no more locks to release!
[  931.051463]

The drm_gpusvm_notifier_unlock() sits under err_free label and the
first jump to err_free is just before calling the
drm_gpusvm_notifier_lock() causing unbalanced unlock.

## References
- https://git.kernel.org/stable/c/8efaa47a871662a8c21b819cec60786f7ef17ab4
- https://git.kernel.org/stable/c/d287dee565c3c32e1ed76ec1847af46809c29b90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63863.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63863
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
