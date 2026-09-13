# [H] ASoC: core: Fix use-after-free in snd_soc_exit()

## Summary
Severity: High
Advisory: CVE-2022-49842
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49842
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.156, >=5.11.0 <5.15.80, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: core: Fix use-after-free in snd_soc_exit()

KASAN reports a use-after-free:

BUG: KASAN: use-after-free in device_del+0xb5b/0xc60
Read of size 8 at addr ffff888008655050 by task rmmod/387
CPU: 2 PID: 387 Comm: rmmod
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
Call Trace:
<TASK>
dump_stack_lvl+0x79/0x9a
print_report+0x17f/0x47b
kasan_report+0xbb/0xf0
device_del+0xb5b/0xc60
platform_device_del.part.0+0x24/0x200
platform_device_unregister+0x2e/0x40
snd_soc_exit+0xa/0x22 [snd_soc_core]
__do_sys_delete_module.constprop.0+0x34f/0x5b0
do_syscall_64+0x3a/0x90
entry_SYSCALL_64_after_hwframe+0x63/0xcd
...
</TASK>

It's bacause in snd_soc_init(), snd_soc_util_init() is possble to fail,
but its ret is ignored, which makes soc_dummy_dev unregistered twice.

snd_soc_init()
    snd_soc_util_init()
        platform_device_register_simple(soc_dummy_dev)
        platform_driver_register() # fail
    	platform_device_unregister(soc_dummy_dev)
    platform_driver_register() # success
...
snd_soc_exit()
    snd_soc_util_exit()
    # soc_dummy_dev will be unregistered for second time

To fix it, handle error and stop snd_soc_init() when util_init() fail.
Also clean debugfs when util_init() or driver_register() fail.

## References
- https://git.kernel.org/stable/c/2ec3f558db343b045a7c7419cdbaec266b8ac1a7
- https://git.kernel.org/stable/c/34eee4189bcebbd5f6a2ff25ef0cb893ad33d51e
- https://git.kernel.org/stable/c/41fad4f712e081acdfde8b59847f9f66eaf407a0
- https://git.kernel.org/stable/c/6ec27c53886c8963729885bcf2dd996eba2767a7
- https://git.kernel.org/stable/c/8d21554ec7680e9585fb852d933203c3db60dad1
- https://git.kernel.org/stable/c/90bbdf30a51e42378cb23a312005a022794b8e1e
- https://git.kernel.org/stable/c/a3365e62239dc064019a244bde5686ac18527c22
- https://git.kernel.org/stable/c/c5674bd073c0fd9f620ca550c5ff08d0d429bdd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49842.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49842
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
