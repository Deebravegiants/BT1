# [H] CVE-2021-47561

## Summary
Severity: High
Advisory: CVE-2021-47561
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47561
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: virtio: disable timeout handling

If a timeout is hit, it can result is incorrect data on the I2C bus
and/or memory corruptions in the guest since the device can still be
operating on the buffers it was given while the guest has freed them.

Here is, for example, the start of a slub_debug splat which was
triggered on the next transfer after one transfer was forced to timeout
by setting a breakpoint in the backend (rust-vmm/vhost-device):

 BUG kmalloc-1k (Not tainted): Poison overwritten
 First byte 0x1 instead of 0x6b
 Allocated in virtio_i2c_xfer+0x65/0x35c age=350 cpu=0 pid=29
 	__kmalloc+0xc2/0x1c9
 	virtio_i2c_xfer+0x65/0x35c
 	__i2c_transfer+0x429/0x57d
 	i2c_transfer+0x115/0x134
 	i2cdev_ioctl_rdwr+0x16a/0x1de
 	i2cdev_ioctl+0x247/0x2ed
 	vfs_ioctl+0x21/0x30
 	sys_ioctl+0xb18/0xb41
 Freed in virtio_i2c_xfer+0x32e/0x35c age=244 cpu=0 pid=29
 	kfree+0x1bd/0x1cc
 	virtio_i2c_xfer+0x32e/0x35c
 	__i2c_transfer+0x429/0x57d
 	i2c_transfer+0x115/0x134
 	i2cdev_ioctl_rdwr+0x16a/0x1de
 	i2cdev_ioctl+0x247/0x2ed
 	vfs_ioctl+0x21/0x30
 	sys_ioctl+0xb18/0xb41

There is no simple fix for this (the driver would have to always create
bounce buffers and hold on to them until the device eventually returns
the buffers), so just disable the timeout support for now.

## References
- https://git.kernel.org/stable/c/84e1d0bf1d7121759622dabf8fbef4c99ad597c5
- https://git.kernel.org/stable/c/cc432b0727ce404cc13e8f6b5ce29f412c3f9f1f
