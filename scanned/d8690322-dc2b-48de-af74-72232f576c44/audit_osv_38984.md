# [H] iommu/amd: move wait_on_sem() out of spinlock

## Summary
Severity: High
Advisory: CVE-2026-43253
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43253
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/amd: move wait_on_sem() out of spinlock

With iommu.strict=1, the existing completion wait path can cause soft
lockups under stressed environment, as wait_on_sem() busy-waits under the
spinlock with interrupts disabled.

Move the completion wait in iommu_completion_wait() out of the spinlock.
wait_on_sem() only polls the hardware-updated cmd_sem and does not require
iommu->lock, so holding the lock during the busy wait unnecessarily
increases contention and extends the time with interrupts disabled.

## References
- https://git.kernel.org/stable/c/496269d12072ecb219826485bdbec70c92a8eef5
- https://git.kernel.org/stable/c/715c263119fd1b918a9fcbd8a36ea5b604a46324
- https://git.kernel.org/stable/c/d2a0cac10597068567d336e85fa3cbdbe8ca62bf
- https://git.kernel.org/stable/c/e15768e68820142077bbca402d8e902f64ade1b0
- https://git.kernel.org/stable/c/f2f65b28d802a667119147444ec2ae33eebf9a58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
