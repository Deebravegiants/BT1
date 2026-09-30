# [H] btrfs: fix use-after-free of block device file in __btrfs_free_extra_devids()

## Summary
Severity: High
Advisory: CVE-2024-50217
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50217
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix use-after-free of block device file in __btrfs_free_extra_devids()

Mounting btrfs from two images (which have the same one fsid and two
different dev_uuids) in certain executing order may trigger an UAF for
variable 'device->bdev_file' in __btrfs_free_extra_devids(). And
following are the details:

1. Attach image_1 to loop0, attach image_2 to loop1, and scan btrfs
   devices by ioctl(BTRFS_IOC_SCAN_DEV):

             /  btrfs_device_1 → loop0
   fs_device
             \  btrfs_device_2 → loop1
2. mount /dev/loop0 /mnt
   btrfs_open_devices
    btrfs_device_1->bdev_file = btrfs_get_bdev_and_sb(loop0)
    btrfs_device_2->bdev_file = btrfs_get_bdev_and_sb(loop1)
   btrfs_fill_super
    open_ctree
     fail: btrfs_close_devices // -ENOMEM
	    btrfs_close_bdev(btrfs_device_1)
             fput(btrfs_device_1->bdev_file)
	      // btrfs_device_1->bdev_file is freed
	    btrfs_close_bdev(btrfs_device_2)
             fput(btrfs_device_2->bdev_file)

3. mount /dev/loop1 /mnt
   btrfs_open_devices
    btrfs_get_bdev_and_sb(&bdev_file)
     // EIO, btrfs_device_1->bdev_file is not assigned,
     // which points to a freed memory area
    btrfs_device_2->bdev_file = btrfs_get_bdev_and_sb(loop1)
   btrfs_fill_super
    open_ctree
     btrfs_free_extra_devids
      if (btrfs_device_1->bdev_file)
       fput(btrfs_device_1->bdev_file) // UAF !

Fix it by setting 'device->bdev_file' as 'NULL' after closing the
btrfs_device in btrfs_close_one_device().

## References
- http://www.openwall.com/lists/oss-security/2025/04/10/4
- http://www.openwall.com/lists/oss-security/2025/04/10/5
- http://www.openwall.com/lists/oss-security/2025/04/10/6
- https://git.kernel.org/stable/c/47a83f8df39545f3f552bb6a1b6d9c30e37621dd
- https://git.kernel.org/stable/c/aec8e6bf839101784f3ef037dcdb9432c3f32343
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50217.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50217
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
