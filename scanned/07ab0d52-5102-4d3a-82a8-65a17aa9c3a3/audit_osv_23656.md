# [M] nbd: fix race between nbd_alloc_config() and module removal

## Summary
Severity: Medium
Advisory: CVE-2022-49300
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49300
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nbd: fix race between nbd_alloc_config() and module removal

When nbd module is being removing, nbd_alloc_config() may be
called concurrently by nbd_genl_connect(), although try_module_get()
will return false, but nbd_alloc_config() doesn't handle it.

The race may lead to the leak of nbd_config and its related
resources (e.g, recv_workq) and oops in nbd_read_stat() due
to the unload of nbd module as shown below:

  BUG: kernel NULL pointer dereference, address: 0000000000000040
  Oops: 0000 [#1] SMP PTI
  CPU: 5 PID: 13840 Comm: kworker/u17:33 Not tainted 5.14.0+ #1
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
  Workqueue: knbd16-recv recv_work [nbd]
  RIP: 0010:nbd_read_stat.cold+0x130/0x1a4 [nbd]
  Call Trace:
   recv_work+0x3b/0xb0 [nbd]
   process_one_work+0x1ed/0x390
   worker_thread+0x4a/0x3d0
   kthread+0x12a/0x150
   ret_from_fork+0x22/0x30

Fixing it by checking the return value of try_module_get()
in nbd_alloc_config(). As nbd_alloc_config() may return ERR_PTR(-ENODEV),
assign nbd->config only when nbd_alloc_config() succeeds to ensure
the value of nbd->config is binary (valid or NULL).

Also adding a debug message to check the reference counter
of nbd_config during module removal.

## References
- https://git.kernel.org/stable/c/122e4adaff2439f1cc18cc7e931980fa7560df5c
- https://git.kernel.org/stable/c/165cf2e0019fa6cedc75b456490c41494c34abb4
- https://git.kernel.org/stable/c/2573f2375b64280be977431701ed5d33b75b9ad0
- https://git.kernel.org/stable/c/2888fa41985f93ed0a6837cfbb06bcbfd7fa2314
- https://git.kernel.org/stable/c/71c142f910da44421213ade601bcbd23ceae19fa
- https://git.kernel.org/stable/c/8a7da4ced236ce6637fe70f14ca18e718d4bf9e9
- https://git.kernel.org/stable/c/c55b2b983b0fa012942c3eb16384b2b722caa810
- https://git.kernel.org/stable/c/d09525720dd5201756f698bee1076de9aefd4602
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49300.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
