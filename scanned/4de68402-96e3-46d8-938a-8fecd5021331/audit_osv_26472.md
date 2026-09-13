# [M] firmware: dmi-sysfs: Fix null-ptr-deref in dmi_sysfs_register_handle

## Summary
Severity: Medium
Advisory: CVE-2023-53250
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53250
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.99, >=5.16.0 <6.1.16, >=5.19.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: dmi-sysfs: Fix null-ptr-deref in dmi_sysfs_register_handle

KASAN reported a null-ptr-deref error:

KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
CPU: 0 PID: 1373 Comm: modprobe
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
RIP: 0010:dmi_sysfs_entry_release
...
Call Trace:
 <TASK>
 kobject_put
 dmi_sysfs_register_handle (drivers/firmware/dmi-sysfs.c:540) dmi_sysfs
 dmi_decode_table (drivers/firmware/dmi_scan.c:133)
 dmi_walk (drivers/firmware/dmi_scan.c:1115)
 dmi_sysfs_init (drivers/firmware/dmi-sysfs.c:149) dmi_sysfs
 do_one_initcall (init/main.c:1296)
 ...
Kernel panic - not syncing: Fatal exception
Kernel Offset: 0x4000000 from 0xffffffff81000000
---[ end Kernel panic - not syncing: Fatal exception ]---

It is because previous patch added kobject_put() to release the memory
which will call  dmi_sysfs_entry_release() and list_del().

However, list_add_tail(entry->list) is called after the error block,
so the list_head is uninitialized and cannot be deleted.

Move error handling to after list_add_tail to fix this.

## References
- https://git.kernel.org/stable/c/18e126e97c961f7a93823795c879d7c085fe5098
- https://git.kernel.org/stable/c/5d0492d1d934642bdfd2057acc1b56f4b57be465
- https://git.kernel.org/stable/c/b4fe158259fb5fead52ff2b55841ec5c39492604
- https://git.kernel.org/stable/c/e851996b32264e78a10863c2ac41a8689d7b9252
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53250.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
