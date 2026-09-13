# [H] cxl/port: Hold port reference until decoder release

## Summary
Severity: High
Advisory: CVE-2022-49223
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49223
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.54, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/port: Hold port reference until decoder release

KASAN + DEBUG_KOBJECT_RELEASE reports a potential use-after-free in
cxl_decoder_release() where it goes to reference its parent, a cxl_port,
to free its id back to port->decoder_ida.

 BUG: KASAN: use-after-free in to_cxl_port+0x18/0x90 [cxl_core]
 Read of size 8 at addr ffff888119270908 by task kworker/35:2/379

 CPU: 35 PID: 379 Comm: kworker/35:2 Tainted: G           OE     5.17.0-rc2+ #198
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 0.0.0 02/06/2015
 Workqueue: events kobject_delayed_cleanup
 Call Trace:
  <TASK>
  dump_stack_lvl+0x59/0x73
  print_address_description.constprop.0+0x1f/0x150
  ? to_cxl_port+0x18/0x90 [cxl_core]
  kasan_report.cold+0x83/0xdf
  ? to_cxl_port+0x18/0x90 [cxl_core]
  to_cxl_port+0x18/0x90 [cxl_core]
  cxl_decoder_release+0x2a/0x60 [cxl_core]
  device_release+0x5f/0x100
  kobject_cleanup+0x80/0x1c0

The device core only guarantees parent lifetime until all children are
unregistered. If a child needs a parent to complete its ->release()
callback that child needs to hold a reference to extend the lifetime of
the parent.

## References
- https://git.kernel.org/stable/c/49f2dab77a5e1354f5da6ccdc9346a8212697be2
- https://git.kernel.org/stable/c/518bb96367123062b48b0a9842f2864249b565f6
- https://git.kernel.org/stable/c/74be98774dfbc5b8b795db726bd772e735d2edd4
- https://git.kernel.org/stable/c/b0022ca445d5fc4d0c89d15dcd0f855977b22c1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49223.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49223
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
