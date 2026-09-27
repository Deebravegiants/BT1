# [M] media: ts2020: fix null-ptr-deref in ts2020_probe()

## Summary
Severity: Medium
Advisory: CVE-2024-56574
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56574
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: ts2020: fix null-ptr-deref in ts2020_probe()

KASAN reported a null-ptr-deref issue when executing the following
command:

  # echo ts2020 0x20 > /sys/bus/i2c/devices/i2c-0/new_device
    KASAN: null-ptr-deref in range [0x0000000000000010-0x0000000000000017]
    CPU: 53 UID: 0 PID: 970 Comm: systemd-udevd Not tainted 6.12.0-rc2+ #24
    Hardware name: QEMU Standard PC (Q35 + ICH9, 2009)
    RIP: 0010:ts2020_probe+0xad/0xe10 [ts2020]
    RSP: 0018:ffffc9000abbf598 EFLAGS: 00010202
    RAX: dffffc0000000000 RBX: 0000000000000000 RCX: ffffffffc0714809
    RDX: 0000000000000002 RSI: ffff88811550be00 RDI: 0000000000000010
    RBP: ffff888109868800 R08: 0000000000000001 R09: fffff52001577eb6
    R10: 0000000000000000 R11: ffffc9000abbff50 R12: ffffffffc0714790
    R13: 1ffff92001577eb8 R14: ffffffffc07190d0 R15: 0000000000000001
    FS:  00007f95f13b98c0(0000) GS:ffff888149280000(0000) knlGS:0000000000000000
    CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
    CR2: 0000555d2634b000 CR3: 0000000152236000 CR4: 00000000000006f0
    DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
    DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
    Call Trace:
     <TASK>
     ts2020_probe+0xad/0xe10 [ts2020]
     i2c_device_probe+0x421/0xb40
     really_probe+0x266/0x850
    ...

The cause of the problem is that when using sysfs to dynamically register
an i2c device, there is no platform data, but the probe process of ts2020
needs to use platform data, resulting in a null pointer being accessed.

Solve this problem by adding checks to platform data.

## References
- https://git.kernel.org/stable/c/4a058b34b52ed3feb1f3ff6fd26aefeeeed20cba
- https://git.kernel.org/stable/c/5a53f97cd5977911850b695add057f9965c1a2d6
- https://git.kernel.org/stable/c/901070571bc191d1d8d7a1379bc5ba9446200999
- https://git.kernel.org/stable/c/a2ed3b780f34e4a6403064208bc2c99d1ed85026
- https://git.kernel.org/stable/c/b6208d1567f929105011bcdfd738f59a6bdc1088
- https://git.kernel.org/stable/c/ced1c04e82e3ecc246b921b9733f0df0866aa50d
- https://git.kernel.org/stable/c/dc03866b5f4aa2668946f8384a1e5286ae53bbaa
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56574.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56574
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
