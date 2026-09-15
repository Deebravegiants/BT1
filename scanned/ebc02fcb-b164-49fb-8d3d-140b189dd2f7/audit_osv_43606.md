# [H] i2c: imx: Cancel hrtimer before clearing slave pointer

## Summary
Severity: High
Advisory: CVE-2026-74461
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74461
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: imx: Cancel hrtimer before clearing slave pointer

In i2c_imx_unreg_slave(), the slave pointer is set to NULL after
disabling interrupts.  However, a pending interrupt might already
have started the hrtimer (i2c_imx_slave_timeout) before the pointer
was cleared.  If the hrtimer fires after i2c_imx->slave is set to
NULL, the timer callback i2c_imx_slave_finish_op() will call
i2c_imx_slave_event() with a NULL slave pointer, which results in a
use-after-free / NULL pointer dereference.

Fix by canceling the hrtimer and waiting for it to complete after
disabling interrupts, before clearing the slave pointer.

## References
- https://git.kernel.org/stable/c/470fe15fb3bb2eba6629be301ca7e991ee3cfb7e
- https://git.kernel.org/stable/c/6ac7702b6cc2b94aaed9ef2d95bfbefcdc90061f
- https://git.kernel.org/stable/c/753060f2b77ff2f386addbd3ecadb95b9f90cddd
- https://git.kernel.org/stable/c/a8a1f9ac3d763e721586f15479ef9140b216ddf3
- https://git.kernel.org/stable/c/affd62f5719a78135b7441aa49c8cab3c3b5e838
- https://git.kernel.org/stable/c/dab4762ee7f3fd0a01980d5407ba48d0261d3bff
- https://git.kernel.org/stable/c/e3da77bdb4015051656bb472c295656bbea03b6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74461.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
