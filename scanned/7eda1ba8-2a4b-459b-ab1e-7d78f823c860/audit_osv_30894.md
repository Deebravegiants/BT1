# [H] brd: defer automatic disk creation until module initialization succeeds

## Summary
Severity: High
Advisory: CVE-2024-56693
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56693
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

brd: defer automatic disk creation until module initialization succeeds

My colleague Wupeng found the following problems during fault injection:

BUG: unable to handle page fault for address: fffffbfff809d073
PGD 6e648067 P4D 123ec8067 PUD 123ec4067 PMD 100e38067 PTE 0
Oops: Oops: 0000 [#1] PREEMPT SMP KASAN NOPTI
CPU: 5 UID: 0 PID: 755 Comm: modprobe Not tainted 6.12.0-rc3+ #17
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
1.16.1-2.fc37 04/01/2014
RIP: 0010:__asan_load8+0x4c/0xa0
...
Call Trace:
 <TASK>
 blkdev_put_whole+0x41/0x70
 bdev_release+0x1a3/0x250
 blkdev_release+0x11/0x20
 __fput+0x1d7/0x4a0
 task_work_run+0xfc/0x180
 syscall_exit_to_user_mode+0x1de/0x1f0
 do_syscall_64+0x6b/0x170
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

loop_init() is calling loop_add() after __register_blkdev() succeeds and
is ignoring disk_add() failure from loop_add(), for loop_add() failure
is not fatal and successfully created disks are already visible to
bdev_open().

brd_init() is currently calling brd_alloc() before __register_blkdev()
succeeds and is releasing successfully created disks when brd_init()
returns an error. This can cause UAF for the latter two case:

case 1:
    T1:
modprobe brd
  brd_init
    brd_alloc(0) // success
      add_disk
        disk_scan_partitions
          bdev_file_open_by_dev // alloc file
          fput // won't free until back to userspace
    brd_alloc(1) // failed since mem alloc error inject
  // error path for modprobe will release code segment
  // back to userspace
  __fput
    blkdev_release
      bdev_release
        blkdev_put_whole
          bdev->bd_disk->fops->release // fops is freed now, UAF!

case 2:
    T1:                            T2:
modprobe brd
  brd_init
    brd_alloc(0) // success
                                   open(/dev/ram0)
    brd_alloc(1) // fail
  // error path for modprobe

                                   close(/dev/ram0)
                                   ...
                                   /* UAF! */
                                   bdev->bd_disk->fops->release

Fix this problem by following what loop_init() does. Besides,
reintroduce brd_devices_mutex to help serialize modifications to
brd_list.

## References
- https://git.kernel.org/stable/c/259bf925583ec9e3781df778cadf00594095090d
- https://git.kernel.org/stable/c/410896624db639500f24f46478b4bfa05c76bf56
- https://git.kernel.org/stable/c/41219c147df8bbd6591f59af5d695fb6c9a1cbff
- https://git.kernel.org/stable/c/63dfd728b30f79495dacc886127695a379805152
- https://git.kernel.org/stable/c/826cc42adf44930a633d11a5993676d85ddb0842
- https://git.kernel.org/stable/c/c0c2744cd2939ec5999c51dbaf2af16886548b7b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56693.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56693
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
