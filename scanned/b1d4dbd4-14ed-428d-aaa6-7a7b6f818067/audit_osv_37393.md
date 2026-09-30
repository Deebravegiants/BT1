# [H] can: isotp: fix tx.buf use-after-free in isotp_sendmsg()

## Summary
Severity: High
Advisory: CVE-2026-31474
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31474
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: isotp: fix tx.buf use-after-free in isotp_sendmsg()

isotp_sendmsg() uses only cmpxchg() on so->tx.state to serialize access
to so->tx.buf. isotp_release() waits for ISOTP_IDLE via
wait_event_interruptible() and then calls kfree(so->tx.buf).

If a signal interrupts the wait_event_interruptible() inside close()
while tx.state is ISOTP_SENDING, the loop exits early and release
proceeds to force ISOTP_SHUTDOWN and continues to kfree(so->tx.buf)
while sendmsg may still be reading so->tx.buf for the final CAN frame
in isotp_fill_dataframe().

The so->tx.buf can be allocated once when the standard tx.buf length needs
to be extended. Move the kfree() of this potentially extended tx.buf to
sk_destruct time when either isotp_sendmsg() and isotp_release() are done.

## References
- https://git.kernel.org/stable/c/2e62e7051eca75a7f2e3d52d62ec10d7d7aa358c
- https://git.kernel.org/stable/c/424e95d62110cdbc8fd12b40918f37e408e35a92
- https://git.kernel.org/stable/c/9649d051e54413049c009638ec1dc23962c884a4
- https://git.kernel.org/stable/c/cb3d6efa78460e6d50bf68806d0db66265709f64
- https://git.kernel.org/stable/c/eec8a1b18a79600bd4419079dc0026c1db72a830
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31474.json
- https://access.redhat.com/errata/RHSA-2026:27288
- https://access.redhat.com/errata/RHSA-2026:27731
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/security/cve/CVE-2026-31474
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31474.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31474
- https://bugzilla.redhat.com/show_bug.cgi?id=2460646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
