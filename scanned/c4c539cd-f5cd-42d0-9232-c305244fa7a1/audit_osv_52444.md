# [M] CVE-2021-47455

## Summary
Severity: Medium
Advisory: CVE-2021-47455
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47455
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: Fix possible memory leak in ptp_clock_register()

I got memory leak as follows when doing fault injection test:

unreferenced object 0xffff88800906c618 (size 8):
  comm "i2c-idt82p33931", pid 4421, jiffies 4294948083 (age 13.188s)
  hex dump (first 8 bytes):
    70 74 70 30 00 00 00 00                          ptp0....
  backtrace:
    [<00000000312ed458>] __kmalloc_track_caller+0x19f/0x3a0
    [<0000000079f6e2ff>] kvasprintf+0xb5/0x150
    [<0000000026aae54f>] kvasprintf_const+0x60/0x190
    [<00000000f323a5f7>] kobject_set_name_vargs+0x56/0x150
    [<000000004e35abdd>] dev_set_name+0xc0/0x100
    [<00000000f20cfe25>] ptp_clock_register+0x9f4/0xd30 [ptp]
    [<000000008bb9f0de>] idt82p33_probe.cold+0x8b6/0x1561 [ptp_idt82p33]

When posix_clock_register() returns an error, the name allocated
in dev_set_name() will be leaked, the put_device() should be used
to give up the device reference, then the name will be freed in
kobject_cleanup() and other memory will be freed in ptp_clock_release().

## References
- https://git.kernel.org/stable/c/f1c96d8085588e1b997a96214b409ac3be20b524
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/4225fea1cb28370086e17e82c0f69bec2779dca0
- https://git.kernel.org/stable/c/95c0a0c5ec8839f8f21672be786e87a100319ca8
