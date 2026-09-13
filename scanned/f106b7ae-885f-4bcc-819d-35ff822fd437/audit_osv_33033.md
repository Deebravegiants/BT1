# [H] Bluetooth: hci_sync: fix double free in 'hci_discovery_filter_clear()'

## Summary
Severity: High
Advisory: CVE-2025-38593
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38593
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: fix double free in 'hci_discovery_filter_clear()'

Function 'hci_discovery_filter_clear()' frees 'uuids' array and then
sets it to NULL. There is a tiny chance of the following race:

'hci_cmd_sync_work()'

 'update_passive_scan_sync()'

   'hci_update_passive_scan_sync()'

     'hci_discovery_filter_clear()'
       kfree(uuids);

       <-------------------------preempted-------------------------------->
                                           'start_service_discovery()'

                                             'hci_discovery_filter_clear()'
                                               kfree(uuids); // DOUBLE FREE

       <-------------------------preempted-------------------------------->

      uuids = NULL;

To fix it let's add locking around 'kfree()' call and NULL pointer
assignment. Otherwise the following backtrace fires:

[ ] ------------[ cut here ]------------
[ ] kernel BUG at mm/slub.c:547!
[ ] Internal error: Oops - BUG: 00000000f2000800 [#1] PREEMPT SMP
[ ] CPU: 3 UID: 0 PID: 246 Comm: bluetoothd Tainted: G O 6.12.19-kernel #1
[ ] Tainted: [O]=OOT_MODULE
[ ] pstate: 60400005 (nZCv daif +PAN -UAO -TCO -DIT -SSBS BTYPE=--)
[ ] pc : __slab_free+0xf8/0x348
[ ] lr : __slab_free+0x48/0x348
...
[ ] Call trace:
[ ]  __slab_free+0xf8/0x348
[ ]  kfree+0x164/0x27c
[ ]  start_service_discovery+0x1d0/0x2c0
[ ]  hci_sock_sendmsg+0x518/0x924
[ ]  __sock_sendmsg+0x54/0x60
[ ]  sock_write_iter+0x98/0xf8
[ ]  do_iter_readv_writev+0xe4/0x1c8
[ ]  vfs_writev+0x128/0x2b0
[ ]  do_writev+0xfc/0x118
[ ]  __arm64_sys_writev+0x20/0x2c
[ ]  invoke_syscall+0x68/0xf0
[ ]  el0_svc_common.constprop.0+0x40/0xe0
[ ]  do_el0_svc+0x1c/0x28
[ ]  el0_svc+0x30/0xd0
[ ]  el0t_64_sync_handler+0x100/0x12c
[ ]  el0t_64_sync+0x194/0x198
[ ] Code: 8b0002e6 eb17031f 54fffbe1 d503201f (d4210000)
[ ] ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/16852eccbdfaf41a666705e3f8be55cf2864c5ca
- https://git.kernel.org/stable/c/2935e556850e9c94d7a00adf14d3cd7fe406ac03
- https://git.kernel.org/stable/c/7ce9bb0b95fc280e9212b8922590c492ca1d9c39
- https://git.kernel.org/stable/c/86f3dcd1f331cfd4fd7ec88906955134ec51afbe
- https://git.kernel.org/stable/c/a351ff6b8ecca4229afaa0d98042bead8de64799
- https://git.kernel.org/stable/c/f8069f34c4c976786ded97498012225af87435d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38593.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38593
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
