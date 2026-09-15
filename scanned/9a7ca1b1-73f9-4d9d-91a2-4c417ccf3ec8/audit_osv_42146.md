# [H] wifi: brcmfmac: drain bus_reset work on device removal

## Summary
Severity: High
Advisory: CVE-2026-64586
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64586
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: brcmfmac: drain bus_reset work on device removal

brcmf_fw_crashed() and the debugfs "reset" entry both schedule
drvr->bus_reset, whose callback recovers drvr through container_of()
and dereferences it.  The removal path frees drvr (brcmf_free ->
wiphy_free) without draining the work, so a bus_reset callback pending
or running during removal can outlive drvr.

Cancellation cannot live in brcmf_detach() or brcmf_free(): the work
callback reaches teardown through the bus .reset op (PCIe
brcmf_pcie_reset -> brcmf_detach; SDIO brcmf_sdio_bus_reset ->
brcmf_sdiod_remove -> brcmf_free), so cancelling there would wait for
the running work and deadlock.

Add a per-bus mutex (bus_reset_lock) and route all arming through
brcmf_bus_schedule_reset(), which under the lock skips when the bus is
marked removing.  Each bus remove entry calls
brcmf_bus_cancel_reset_work(), which under the same lock sets removing
and cancels the work.  Holding the mutex across cancel_work_sync() makes
the set-removing + drain step atomic.  Every producer reaches the arming
path from process context -- the PCIe firmware-halt notification runs in
the threaded IRQ handler (brcmf_pcie_isr_thread) and the SDIO hostmail
path runs from the data workqueue -- so the mutex is taken only in
sleepable contexts.  Where applicable the remove entry first stops the
firmware-crash producer: on PCIe mask the mailbox and synchronize_irq;
on SDIO unregister the bus interrupt and cancel the data worker, which
also reports firmware halts through brcmf_fw_crashed().  The mutex is
initialized at bus allocation.  The SDIO suspend power-off path frees
drvr through the same brcmf_sdiod_remove() and takes the same lock;
resume re-allows the work only on a successful re-probe.

Also guard brcmf_fw_crashed() against a NULL bus_if/drvr: it can fire
before brcmf_attach() wires up drvr, and it dereferences drvr
(bphy_err/brcmf_dev_coredump) before reaching the arming gate.

The bus_reset work is shared across buses, so the drain is applied to
every remove path: PCIe (the .reset op introduced by the Fixes commit),
SDIO (arms the same work through brcmf_fw_crashed()), and USB (via the
debugfs "reset" entry).  cancel_work_sync() drains a running or pending
bus_reset work item before removal frees drvr, and patch 1/2 makes the
scratch-buffer release safe when reset teardown has already released
those DMA buffers.

This patch fixes the lifetime of the bus_reset work item itself.  It does
not attempt to address the separate, pre-existing lifetime of the
asynchronous firmware completion started by the PCIe reset path.  That
callback needs its own lifetime/ownership protocol and is being tracked
separately.

This issue was found by an in-house static analysis tool.

## References
- https://git.kernel.org/stable/c/02d378828af8bb74f6c2f4d2bee3c77cf16c861e
- https://git.kernel.org/stable/c/177a25be1195f8bdc6160ba5f1a5699f7041c985
- https://git.kernel.org/stable/c/43b25879f004c98defa2776bedc6ca4763c51945
- https://git.kernel.org/stable/c/4824e3bcc68f8d678b409039d1bb48c7b5ea73dc
- https://git.kernel.org/stable/c/61127dd20920bf28460a1609aabb0dafa2f54fac
- https://git.kernel.org/stable/c/9dfb09cb0abbf92a06f93e0715e163aa188a84da
- https://git.kernel.org/stable/c/c268331845ee00dbdbccb000826bb612dff2bee7
- https://git.kernel.org/stable/c/e3815d1ffbb9be4f1605ddc3b427557893461683
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64586.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
