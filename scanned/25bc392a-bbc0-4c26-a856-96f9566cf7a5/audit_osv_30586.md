# [M] wifi: rtlwifi: Drastically reduce the attempts to read efuse in case of failures

## Summary
Severity: Medium
Advisory: CVE-2024-53190
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53190
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtlwifi: Drastically reduce the attempts to read efuse in case of failures

Syzkaller reported a hung task with uevent_show() on stack trace. That
specific issue was addressed by another commit [0], but even with that
fix applied (for example, running v6.12-rc5) we face another type of hung
task that comes from the same reproducer [1]. By investigating that, we
could narrow it to the following path:

(a) Syzkaller emulates a Realtek USB WiFi adapter using raw-gadget and
dummy_hcd infrastructure.

(b) During the probe of rtl8192cu, the driver ends-up performing an efuse
read procedure (which is related to EEPROM load IIUC), and here lies the
issue: the function read_efuse() calls read_efuse_byte() many times, as
loop iterations depending on the efuse size (in our example, 512 in total).

This procedure for reading efuse bytes relies in a loop that performs an
I/O read up to *10k* times in case of failures. We measured the time of
the loop inside read_efuse_byte() alone, and in this reproducer (which
involves the dummy_hcd emulation layer), it takes 15 seconds each. As a
consequence, we have the driver stuck in its probe routine for big time,
exposing a stack trace like below if we attempt to reboot the system, for
example:

task:kworker/0:3 state:D stack:0 pid:662 tgid:662 ppid:2 flags:0x00004000
Workqueue: usb_hub_wq hub_event
Call Trace:
 __schedule+0xe22/0xeb6
 schedule_timeout+0xe7/0x132
 __wait_for_common+0xb5/0x12e
 usb_start_wait_urb+0xc5/0x1ef
 ? usb_alloc_urb+0x95/0xa4
 usb_control_msg+0xff/0x184
 _usbctrl_vendorreq_sync+0xa0/0x161
 _usb_read_sync+0xb3/0xc5
 read_efuse_byte+0x13c/0x146
 read_efuse+0x351/0x5f0
 efuse_read_all_map+0x42/0x52
 rtl_efuse_shadow_map_update+0x60/0xef
 rtl_get_hwinfo+0x5d/0x1c2
 rtl92cu_read_eeprom_info+0x10a/0x8d5
 ? rtl92c_read_chip_version+0x14f/0x17e
 rtl_usb_probe+0x323/0x851
 usb_probe_interface+0x278/0x34b
 really_probe+0x202/0x4a4
 __driver_probe_device+0x166/0x1b2
 driver_probe_device+0x2f/0xd8
 [...]

We propose hereby to drastically reduce the attempts of doing the I/O
reads in case of failures, restricted to USB devices (given that
they're inherently slower than PCIe ones). By retrying up to 10 times
(instead of 10000), we got reponsiveness in the reproducer, while seems
reasonable to believe that there's no sane USB device implementation in
the field requiring this amount of retries at every I/O read in order
to properly work. Based on that assumption, it'd be good to have it
backported to stable but maybe not since driver implementation (the 10k
number comes from day 0), perhaps up to 6.x series makes sense.

[0] Commit 15fffc6a5624 ("driver core: Fix uevent_show() vs driver detach race")

[1] A note about that: this syzkaller report presents multiple reproducers
that differs by the type of emulated USB device. For this specific case,
check the entry from 2024/08/08 06:23 in the list of crashes; the C repro
is available at https://syzkaller.appspot.com/text?tag=ReproC&x=1521fc83980000.

## References
- https://git.kernel.org/stable/c/5c1b544563005a00591a3aa86ecff62ed4d11be3
- https://git.kernel.org/stable/c/8f3551f67991652c83469c7dd51d7b9b187b265f
- https://git.kernel.org/stable/c/ac064c656f105b9122bc43991a170f95f72b7a43
- https://git.kernel.org/stable/c/c386fb76f01794f1023d01a6ec5f5c93d00acd3b
- https://git.kernel.org/stable/c/eeb0b9b9e66b0b54cdad8e1c1cf0f55e8ba4211c
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53190.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53190
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
