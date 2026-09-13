# [H] vsock/virtio: avoid refilling the RX queue after teardown

## Summary
Severity: High
Advisory: CVE-2026-74613
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74613
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: avoid refilling the RX queue after teardown

Commit b917507e5ad9 ("vsock/virtio: stop workers during the .remove()")
made the RX worker jump to its common exit when rx_run is clear.  That
exit still refills the RX queue when the buffer count is low, so work
queued across virtio_vsock_vqs_del() can add buffers after the virtqueues
have been deleted.

BUG: KASAN: slab-use-after-free in virtqueue_add_sgs
Read of size 4 by task kworker/0:1
Workqueue: virtio_vsock virtio_transport_rx_work
Call Trace:
 virtqueue_add_sgs (drivers/virtio/virtio_ring.c:2796)
 virtio_vsock_rx_fill (net/vmw_vsock/virtio_transport.c:332)
 virtio_transport_rx_work (net/vmw_vsock/virtio_transport.c:701)
 process_one_work (kernel/workqueue.c:3314)
 worker_thread (kernel/workqueue.c:3478)
 kthread (kernel/kthread.c:436)
 ret_from_fork (arch/x86/kernel/process.c:158)
 ret_from_fork_asm (arch/x86/entry/entry_64.S:245)
...
Freed by task 141:
 kfree (mm/slub.c:6566)
 vp_del_vq (drivers/virtio/virtio_pci_common.c:259)
 vp_del_vqs (drivers/virtio/virtio_pci_common.c:285)
 virtio_vsock_freeze (net/vmw_vsock/virtio_transport.c:912)
 virtio_device_freeze (drivers/virtio/virtio.c:658)
 virtio_pci_freeze (drivers/virtio/virtio_pci_common.c:601)
 pci_pm_freeze (drivers/pci/pci-driver.c:1098)
 device_suspend (drivers/base/power/main.c:1968)
Kernel panic - not syncing: KASAN: panic_on_warn set ...

Jump to a no-refill exit when rx_run is clear, leaving the normal exit
to replenish a running queue.

## References
- https://git.kernel.org/stable/c/1aa21e7c8702a7c37cd7d3cace1a652cfa5e8171
- https://git.kernel.org/stable/c/38c7763fdc533edb34dc8f4489c260e8ba2ccae9
- https://git.kernel.org/stable/c/4d37e3525cc346a1421c1bdeaad5848e249fc60c
- https://git.kernel.org/stable/c/9d80a04129a6c27a690cb69de3fe3f50be5aa8b9
- https://git.kernel.org/stable/c/a309b74e3fc052352ab778500449cb9c3853c363
- https://git.kernel.org/stable/c/a31e0ad444698d8aa7534a0f89fda543730f97a5
- https://git.kernel.org/stable/c/a7658508f5fe8f1077a65e8cb9535d3426f37a2f
- https://git.kernel.org/stable/c/e82a5faea2e3886dfb2a65ce092a132e7e896915
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74613.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74613
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
