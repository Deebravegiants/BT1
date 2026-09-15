# [H] i3c: mipi-i3c-hci: Correct RING_CTRL_ABORT handling in DMA dequeue

## Summary
Severity: High
Advisory: CVE-2026-43352
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43352
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: mipi-i3c-hci: Correct RING_CTRL_ABORT handling in DMA dequeue

The logic used to abort the DMA ring contains several flaws:

 1. The driver unconditionally issues a ring abort even when the ring has
    already stopped.
 2. The completion used to wait for abort completion is never
    re-initialized, resulting in incorrect wait behavior.
 3. The abort sequence unintentionally clears RING_CTRL_ENABLE, which
    resets hardware ring pointers and disrupts the controller state.
 4. If the ring is already stopped, the abort operation should be
    considered successful without attempting further action.

Fix the abort handling by checking whether the ring is running before
issuing an abort, re-initializing the completion when needed, ensuring that
RING_CTRL_ENABLE remains asserted during abort, and treating an already
stopped ring as a successful condition.

## References
- https://git.kernel.org/stable/c/003df94bcc9227e8e930abd03ac7f63ac10033dc
- https://git.kernel.org/stable/c/5549611888f5ca2db5e8e692b57f30626ddf9898
- https://git.kernel.org/stable/c/b795e68bf3073d67bebbb5a44d93f49efc5b8cc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43352.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43352
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
