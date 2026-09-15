# [H] video: fbdev: sm712fb: Fix crash in smtcfb_write()

## Summary
Severity: High
Advisory: CVE-2022-49162
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49162
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

video: fbdev: sm712fb: Fix crash in smtcfb_write()

When the sm712fb driver writes three bytes to the framebuffer, the
driver will crash:

    BUG: unable to handle page fault for address: ffffc90001ffffff
    RIP: 0010:smtcfb_write+0x454/0x5b0
    Call Trace:
     vfs_write+0x291/0xd60
     ? do_sys_openat2+0x27d/0x350
     ? __fget_light+0x54/0x340
     ksys_write+0xce/0x190
     do_syscall_64+0x43/0x90
     entry_SYSCALL_64_after_hwframe+0x44/0xae

Fix it by removing the open-coded endianness fixup-code.

## References
- https://git.kernel.org/stable/c/0ec746674296c94137f074309c26d17e644c0498
- https://git.kernel.org/stable/c/1aea36a62f0a0ad67eccc945bac0bd6422ef720f
- https://git.kernel.org/stable/c/3b36c05f68ba32d0dfb63abc9016d6fe9117829f
- https://git.kernel.org/stable/c/4f01d09b2bbfbcb47b3eb305560a7f4857a32260
- https://git.kernel.org/stable/c/809b8cde86320698661eec677222bc5c5df76176
- https://git.kernel.org/stable/c/aeb635b49530b7d19e140949753409f759ba99be
- https://git.kernel.org/stable/c/b1c28577529cdfad40c8242673285f1e1e4c314e
- https://git.kernel.org/stable/c/eae90015d10f0c9a47fc4adccba4cd79dce664e4
- https://git.kernel.org/stable/c/fb791514acf9070225eed46e1ccbb0aa7aae5da5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49162.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
