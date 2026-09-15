# [H] drm: bridge: adv7511: unregister cec i2c device after cec adapter

## Summary
Severity: High
Advisory: CVE-2022-50412
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50412
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.234, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: bridge: adv7511: unregister cec i2c device after cec adapter

cec_unregister_adapter() assumes that the underlying adapter ops are
callable. For example, if the CEC adapter currently has a valid physical
address, then the unregistration procedure will invalidate the physical
address by setting it to f.f.f.f. Whence the following kernel oops
observed after removing the adv7511 module:

    Unable to handle kernel execution of user memory at virtual address 0000000000000000
    Internal error: Oops: 86000004 [#1] PREEMPT_RT SMP
    Call trace:
     0x0
     adv7511_cec_adap_log_addr+0x1ac/0x1c8 [adv7511]
     cec_adap_unconfigure+0x44/0x90 [cec]
     __cec_s_phys_addr.part.0+0x68/0x230 [cec]
     __cec_s_phys_addr+0x40/0x50 [cec]
     cec_unregister_adapter+0xb4/0x118 [cec]
     adv7511_remove+0x60/0x90 [adv7511]
     i2c_device_remove+0x34/0xe0
     device_release_driver_internal+0x114/0x1f0
     driver_detach+0x54/0xe0
     bus_remove_driver+0x60/0xd8
     driver_unregister+0x34/0x60
     i2c_del_driver+0x2c/0x68
     adv7511_exit+0x1c/0x67c [adv7511]
     __arm64_sys_delete_module+0x154/0x288
     invoke_syscall+0x48/0x100
     el0_svc_common.constprop.0+0x48/0xe8
     do_el0_svc+0x28/0x88
     el0_svc+0x1c/0x50
     el0t_64_sync_handler+0xa8/0xb0
     el0t_64_sync+0x15c/0x160
    Code: bad PC value
    ---[ end trace 0000000000000000 ]---

Protect against this scenario by unregistering i2c_cec after
unregistering the CEC adapter. Duly disable the CEC clock afterwards
too.

## References
- https://git.kernel.org/stable/c/3747465c5da7a11957a34bbb9485d9fc253b91cc
- https://git.kernel.org/stable/c/40cdb02cb9f965732eb543d47f15bef8d10f0f5f
- https://git.kernel.org/stable/c/4d4d5bc659206b187263190ad9a03513f625659d
- https://git.kernel.org/stable/c/86ae5170786aea3e1751123ca55700fb9b37b623
- https://git.kernel.org/stable/c/f369fb4deed7ab997cfa703dc85ec08b3adc1af8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50412.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
