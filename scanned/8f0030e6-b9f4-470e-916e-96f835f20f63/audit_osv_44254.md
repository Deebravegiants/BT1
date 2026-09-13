# [H] i2c: imx: Fix slave registration race and error handling

## Summary
Severity: High
Advisory: CVE-2026-80678
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80678
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.217, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: imx: Fix slave registration race and error handling

In i2c_imx_reg_slave(), the slave pointer was assigned before
pm_runtime_resume_and_get().  If pm_runtime_resume_and_get() failed,
the error path returned without clearing i2c_imx->slave, leaving it
non-NULL and causing all subsequent registration attempts to fail
with -EBUSY.

Additionally, because this driver uses a shared IRQ, the interrupt
handler i2c_imx_isr() can execute concurrently and, after acquiring
slave_lock, dereference i2c_imx->slave.  The previous fix attempt
added a lockless i2c_imx->slave = NULL on the error path, but that
could race with the ISR under the lock and still cause a NULL pointer
dereference.

Fix both issues by deferring the assignment of i2c_imx->slave and
i2c_imx->last_slave_event to after a successful resume, and by
performing the assignment inside the slave_lock critical section.
This guarantees that the slave pointer is never left stale on the
error path and is always valid when observed by the interrupt handler.

## References
- https://git.kernel.org/stable/c/12a4f0950a158d98552cbaeacc35edccd8d975fa
- https://git.kernel.org/stable/c/614ca6594e301ff682999797c2216e9685558a2b
- https://git.kernel.org/stable/c/754bc62f72fd64b202462367134ac8ce95b005de
- https://git.kernel.org/stable/c/b9f6f4883b9ac86654e75899d0dbf8a7a96ad5d8
- https://git.kernel.org/stable/c/cfdf6e13518589f911b7eace6ccb788e4ed87397
- https://git.kernel.org/stable/c/d64ec362c369bbc33833f7936d5f3a706b0d5c45
- https://git.kernel.org/stable/c/d6748f6802f3eebafaa16a5e5dcfbfb9b3bc173f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80678.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
