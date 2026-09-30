# [H] usb: gadget: udc: bdc: free IRQ and drain func_wake_notify before teardown

## Summary
Severity: High
Advisory: CVE-2026-64583
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64583
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.266, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: udc: bdc: free IRQ and drain func_wake_notify before teardown

The Broadcom BDC UDC driver registers its IRQ handler with
devm_request_irq() in bdc_udc_init(), so the IRQ is released by devm
only after bdc_remove() returns.  devm releases resources in reverse
LIFO order, but bdc_remove() runs bdc_udc_exit() and bdc_hw_exit() ->
bdc_mem_free() manually before returning: bdc_udc_exit() tears down
individual endpoint objects via bdc_free_ep(), while bdc_hw_exit() ->
bdc_mem_free() frees and NULLs the DMA-coherent status-report ring
(bdc->srr.sr_bds) and kfree()s bdc->bdc_ep_array.  Both happen while
the IRQ handler (bdc_udc_interrupt, requested with IRQF_SHARED)
remains deliverable in the window up to the post-remove devm
free_irq().

On receipt of a shared interrupt in that window, bdc_udc_interrupt()
dereferences bdc->srr.sr_bds[bdc->srr.dqp_index] (NULL or freed DMA)
and dispatches sr_handler callbacks that index into bdc_ep_array,
causing a NULL-deref or use-after-free.

The same window affects the delayed_work bdc->func_wake_notify, which is
armed from the IRQ handler via bdc_sr_uspc() -> handle_link_state_change()
-> schedule_delayed_work() and may self-rearm from its own callback
bdc_func_wake_timer().  No cancel exists anywhere in the driver, so a
queued work item that fires after bdc_remove() returns and the bdc
structure is devm-freed dereferences freed memory.

Replace devm_request_irq() with request_irq() and add an explicit
free_irq(bdc->irq, bdc) in bdc_remove().  Clear BDC_GIE before
free_irq() to stop the device from asserting interrupts, then
free_irq() drains any in-flight handler, then cancel_delayed_work_sync()
drains the func_wake_notify delayed work.  This ordering ensures the
IRQ handler and delayed work cannot interfere with the subsequent
endpoint and DMA teardown in bdc_udc_exit() and bdc_hw_exit().  Wire the
matching free_irq() into the bdc_udc_init() error path so the IRQ is
released on probe failure, and route the bdc_init_ep() failure through
err0 instead of returning directly.

This issue was found by an in-house static analysis tool.

## References
- https://git.kernel.org/stable/c/0583f2fbf8f86ae3a0ce054f96783dd83e65d9bb
- https://git.kernel.org/stable/c/0b0b76e31b3991a899ae724eb97d359de0c0f1b1
- https://git.kernel.org/stable/c/1a1d7158420df6b8fa1efc0cdd6ab704801a4fc8
- https://git.kernel.org/stable/c/3fe181952b8a1aeb167d4503c794c0f5050f08ed
- https://git.kernel.org/stable/c/d4964a74717107697999f48bcb4e80a9c0679a27
- https://git.kernel.org/stable/c/dcf3e2f164435b5844706cb8eefef29ebee0eedb
- https://git.kernel.org/stable/c/eac1107e54679db2df2c36d8bba3b66d3ab6cbcd
- https://git.kernel.org/stable/c/f6fc21ec7ccd83726ba766d73d0b8cc03e726475
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64583.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64583
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
