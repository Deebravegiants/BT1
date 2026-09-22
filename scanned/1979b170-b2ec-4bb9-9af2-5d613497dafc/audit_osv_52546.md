# [H] CVE-2021-47564

## Summary
Severity: High
Advisory: CVE-2021-47564
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47564
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: marvell: prestera: fix double free issue on err path

fix error path handling in prestera_bridge_port_join() that
cases prestera driver to crash (see below).

 Trace:
   Internal error: Oops: 96000044 [#1] SMP
   Modules linked in: prestera_pci prestera uio_pdrv_genirq
   CPU: 1 PID: 881 Comm: ip Not tainted 5.15.0 #1
   pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
   pc : prestera_bridge_destroy+0x2c/0xb0 [prestera]
   lr : prestera_bridge_port_join+0x2cc/0x350 [prestera]
   sp : ffff800011a1b0f0
   ...
   x2 : ffff000109ca6c80 x1 : dead000000000100 x0 : dead000000000122
    Call trace:
   prestera_bridge_destroy+0x2c/0xb0 [prestera]
   prestera_bridge_port_join+0x2cc/0x350 [prestera]
   prestera_netdev_port_event.constprop.0+0x3c4/0x450 [prestera]
   prestera_netdev_event_handler+0xf4/0x110 [prestera]
   raw_notifier_call_chain+0x54/0x80
   call_netdevice_notifiers_info+0x54/0xa0
   __netdev_upper_dev_link+0x19c/0x380

## References
- https://git.kernel.org/stable/c/03e5203d2161a00afe4d97d206d2293e40b2f253
- https://git.kernel.org/stable/c/5dca8eff4627315df98feec09fff9dfe3356325e
- https://git.kernel.org/stable/c/e8d032507cb7912baf1d3e0af54516f823befefd
