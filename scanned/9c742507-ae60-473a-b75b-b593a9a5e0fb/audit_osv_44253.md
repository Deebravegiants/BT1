# [H] driver core: use READ_ONCE() for dev->driver in dev_has_sync_state()

## Summary
Severity: High
Advisory: CVE-2026-80677
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80677
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver core: use READ_ONCE() for dev->driver in dev_has_sync_state()

dev_has_sync_state() reads dev->driver twice without holding
device_lock() -- once for the NULL check and once to dereference
->sync_state. Some callers only hold device_links_write_lock, which
doesn't prevent a concurrent unbind from clearing dev->driver via
device_unbind_cleanup().

Fix it by reading dev->driver exactly once with READ_ONCE(), pairing
with the WRITE_ONCE() in device_set_driver().

## References
- https://git.kernel.org/stable/c/358697929351f619143f59c6a8a15a4994748b79
- https://git.kernel.org/stable/c/51b3e1de53ee5b7775c7ff90e67fdb2665fce938
- https://git.kernel.org/stable/c/5e79e0180515b31b2e2244dc3d256fd8b5a07021
- https://git.kernel.org/stable/c/860885fcd2611bca8c28dac8b2c1c7ff160f763e
- https://git.kernel.org/stable/c/89789e4c141904506163dcb91c7289a074573931
- https://git.kernel.org/stable/c/9b0f4082a09760939588135d60a8e9cc994bfa3e
- https://git.kernel.org/stable/c/cc77f0d91e3214e4292208f02a1dc09a31f9aac7
- https://git.kernel.org/stable/c/e9506871a8ea304cde48ff4a57226df2aadddae3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80677.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80677
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
