# [C] RDMA/irdma: Fix data race on CQP request done

## Summary
Severity: Critical
Advisory: CVE-2023-54292
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54292
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.124, >=5.16.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix data race on CQP request done

KCSAN detects a data race on cqp_request->request_done memory location
which is accessed locklessly in irdma_handle_cqp_op while being
updated in irdma_cqp_ce_handler.

Annotate lockless intent with READ_ONCE/WRITE_ONCE to avoid any
compiler optimizations like load fusing and/or KCSAN warning.

[222808.417128] BUG: KCSAN: data-race in irdma_cqp_ce_handler [irdma] / irdma_wait_event [irdma]

[222808.417532] write to 0xffff8e44107019dc of 1 bytes by task 29658 on cpu 5:
[222808.417610]  irdma_cqp_ce_handler+0x21e/0x270 [irdma]
[222808.417725]  cqp_compl_worker+0x1b/0x20 [irdma]
[222808.417827]  process_one_work+0x4d1/0xa40
[222808.417835]  worker_thread+0x319/0x700
[222808.417842]  kthread+0x180/0x1b0
[222808.417852]  ret_from_fork+0x22/0x30

[222808.417918] read to 0xffff8e44107019dc of 1 bytes by task 29688 on cpu 1:
[222808.417995]  irdma_wait_event+0x1e2/0x2c0 [irdma]
[222808.418099]  irdma_handle_cqp_op+0xae/0x170 [irdma]
[222808.418202]  irdma_cqp_cq_destroy_cmd+0x70/0x90 [irdma]
[222808.418308]  irdma_puda_dele_rsrc+0x46d/0x4d0 [irdma]
[222808.418411]  irdma_rt_deinit_hw+0x179/0x1d0 [irdma]
[222808.418514]  irdma_ib_dealloc_device+0x11/0x40 [irdma]
[222808.418618]  ib_dealloc_device+0x2a/0x120 [ib_core]
[222808.418823]  __ib_unregister_device+0xde/0x100 [ib_core]
[222808.418981]  ib_unregister_device+0x22/0x40 [ib_core]
[222808.419142]  irdma_ib_unregister_device+0x70/0x90 [irdma]
[222808.419248]  i40iw_close+0x6f/0xc0 [irdma]
[222808.419352]  i40e_client_device_unregister+0x14a/0x180 [i40e]
[222808.419450]  i40iw_remove+0x21/0x30 [irdma]
[222808.419554]  auxiliary_bus_remove+0x31/0x50
[222808.419563]  device_remove+0x69/0xb0
[222808.419572]  device_release_driver_internal+0x293/0x360
[222808.419582]  driver_detach+0x7c/0xf0
[222808.419592]  bus_remove_driver+0x8c/0x150
[222808.419600]  driver_unregister+0x45/0x70
[222808.419610]  auxiliary_driver_unregister+0x16/0x30
[222808.419618]  irdma_exit_module+0x18/0x1e [irdma]
[222808.419733]  __do_sys_delete_module.constprop.0+0x1e2/0x310
[222808.419745]  __x64_sys_delete_module+0x1b/0x30
[222808.419755]  do_syscall_64+0x39/0x90
[222808.419763]  entry_SYSCALL_64_after_hwframe+0x63/0xcd

[222808.419829] value changed: 0x01 -> 0x03

## References
- https://git.kernel.org/stable/c/5986e96be7d0b82e50a9c6b019ea3f1926fd8764
- https://git.kernel.org/stable/c/b8b90ba636e3861665aef9a3eab5fcf92839a2c5
- https://git.kernel.org/stable/c/c5b5dbcbf91f769b8eb25f88e32a1522f920f37a
- https://git.kernel.org/stable/c/f0842bb3d38863777e3454da5653d80b5fde6321
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54292.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
