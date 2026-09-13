# [H] staging: nvec: fix use-after-free in nvec_rx_completed()

## Summary
Severity: High
Advisory: CVE-2026-72489
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72489
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: nvec: fix use-after-free in nvec_rx_completed()

In nvec_rx_completed(), when an incomplete RX transfer is detected,
nvec_msg_free() is called to return the message back to the pool by
clearing its 'used' atomic flag. Immediately after this, the code
accesses nvec->rx->data[0] to check the message type.

Since nvec_msg_free() marks the pool slot as available via atomic_set(),
any concurrent or subsequent call to nvec_msg_alloc() could claim that
same slot and overwrite its data[] array. Reading nvec->rx->data[0] after
freeing the message is therefore a use-after-free.

Fix this by saving the message type byte before calling nvec_msg_free(),
then using the saved value for the battery quirk check.

## References
- https://git.kernel.org/stable/c/08626fcfe12308ca3f8b22c538ba7dee0b2dce7a
- https://git.kernel.org/stable/c/26813881181deb3a32fbb59eadb2599cbe8423f6
- https://git.kernel.org/stable/c/5de04caa46b635e180cecbd164e333eca535db94
- https://git.kernel.org/stable/c/6b2ea886ebdae44a2394029844a4e78f58e1587d
- https://git.kernel.org/stable/c/9f7fe4165a1f1014bdadc8e744c0fd3c2d8c0b89
- https://git.kernel.org/stable/c/a37625c7b688fcf68a54263528eccbabfd7fa17a
- https://git.kernel.org/stable/c/bb3d592c7d6c4ec8ac6640c690ca13298e7e8e90
- https://git.kernel.org/stable/c/f19a5bc059051143c489dd6f79a0f9c3bfd13aea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72489.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72489
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
