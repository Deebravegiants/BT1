# [H] usb: gadget: f_ncm: Refactor bind path to use __free()

## Summary
Severity: High
Advisory: CVE-2025-40092
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-40092
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: f_ncm: Refactor bind path to use __free()

After an bind/unbind cycle, the ncm->notify_req is left stale. If a
subsequent bind fails, the unified error label attempts to free this
stale request, leading to a NULL pointer dereference when accessing
ep->ops->free_request.

Refactor the error handling in the bind path to use the __free()
automatic cleanup mechanism.

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000020
Call trace:
 usb_ep_free_request+0x2c/0xec
 ncm_bind+0x39c/0x3dc
 usb_add_function+0xcc/0x1f0
 configfs_composite_bind+0x468/0x588
 gadget_bind_driver+0x104/0x270
 really_probe+0x190/0x374
 __driver_probe_device+0xa0/0x12c
 driver_probe_device+0x3c/0x218
 __device_attach_driver+0x14c/0x188
 bus_for_each_drv+0x10c/0x168
 __device_attach+0xfc/0x198
 device_initial_probe+0x14/0x24
 bus_probe_device+0x94/0x11c
 device_add+0x268/0x48c
 usb_add_gadget+0x198/0x28c
 dwc3_gadget_init+0x700/0x858
 __dwc3_set_mode+0x3cc/0x664
 process_scheduled_works+0x1d8/0x488
 worker_thread+0x244/0x334
 kthread+0x114/0x1bc
 ret_from_fork+0x10/0x20

## References
- https://git.kernel.org/stable/c/185193a4714aa9c78437a7a1858fbe5771f0f45c
- https://git.kernel.org/stable/c/1cde4516295a030cb8ab4c93114ca3b6c3c6a1e2
- https://git.kernel.org/stable/c/75a5b8d4ddd4eb6b16cb0b475d14ff4ae64295ef
- https://git.kernel.org/stable/c/d3fe7143928d8dfa2ec7bac9f906b48bc75b98ee
- https://git.kernel.org/stable/c/ed78f4d6079d872432b1ed54f155ef61965d3137
- https://git.kernel.org/stable/c/f37de8dec6a4c379b4b8486003a1de00ff8cff3b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40092.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40092
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
