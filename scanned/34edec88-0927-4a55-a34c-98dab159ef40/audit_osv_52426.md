# [M] CVE-2021-47436

## Summary
Severity: Medium
Advisory: CVE-2021-47436
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47436
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: musb: dsps: Fix the probe error path

Commit 7c75bde329d7 ("usb: musb: musb_dsps: request_irq() after
initializing musb") has inverted the calls to
dsps_setup_optional_vbus_irq() and dsps_create_musb_pdev() without
updating correctly the error path. dsps_create_musb_pdev() allocates and
registers a new platform device which must be unregistered and freed
with platform_device_unregister(), and this is missing upon
dsps_setup_optional_vbus_irq() error.

While on the master branch it seems not to trigger any issue, I observed
a kernel crash because of a NULL pointer dereference with a v5.10.70
stable kernel where the patch mentioned above was backported. With this
kernel version, -EPROBE_DEFER is returned the first time
dsps_setup_optional_vbus_irq() is called which triggers the probe to
error out without unregistering the platform device. Unfortunately, on
the Beagle Bone Black Wireless, the platform device still living in the
system is being used by the USB Ethernet gadget driver, which during the
boot phase triggers the crash.

My limited knowledge of the musb world prevents me to revert this commit
which was sent to silence a robot warning which, as far as I understand,
does not make sense. The goal of this patch was to prevent an IRQ to
fire before the platform device being registered. I think this cannot
ever happen due to the fact that enabling the interrupts is done by the
->enable() callback of the platform musb device, and this platform
device must be already registered in order for the core or any other
user to use this callback.

Hence, I decided to fix the error path, which might prevent future
errors on mainline kernels while also fixing older ones.

## References
- https://git.kernel.org/stable/c/5ed60a430fb5f3d93e7fef66264daef466b4d10c
- https://git.kernel.org/stable/c/9ab5d539bc975b8dcde86eca1b58d836b657732e
- https://git.kernel.org/stable/c/9d89e287116796bf987cc48f5c8632ef3048f8eb
- https://git.kernel.org/stable/c/c2115b2b16421d93d4993f3fe4c520e91d6fe801
- https://git.kernel.org/stable/c/e923bce31ffefe4f60edfc6b84f62d4a858f3676
- https://git.kernel.org/stable/c/ff9249aab39820be11b6975a10d94253b7d426fc
