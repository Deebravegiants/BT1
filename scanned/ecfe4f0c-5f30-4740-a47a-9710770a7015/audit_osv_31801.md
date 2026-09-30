# [H] HID: corsair-void: Add missing delayed work cancel for headset status

## Summary
Severity: High
Advisory: CVE-2025-21797
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21797
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: corsair-void: Add missing delayed work cancel for headset status

The cancel_delayed_work_sync() call was missed, causing a use-after-free
in corsair_void_remove().

## References
- https://git.kernel.org/stable/c/2dcb56a0a4da6946f6c18288da595c13e0d2af86
- https://git.kernel.org/stable/c/48e487b002891eb0aeaec704c9bed51f028deff1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21797.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21797
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
