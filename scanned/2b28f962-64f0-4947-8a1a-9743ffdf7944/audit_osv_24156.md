# [M] media: cx88: Fix a null-ptr-deref bug in buffer_prepare()

## Summary
Severity: Medium
Advisory: CVE-2022-50359
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50359
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: cx88: Fix a null-ptr-deref bug in buffer_prepare()

When the driver calls cx88_risc_buffer() to prepare the buffer, the
function call may fail, resulting in a empty buffer and null-ptr-deref
later in buffer_queue().

The following log can reveal it:

[   41.822762] general protection fault, probably for non-canonical address 0xdffffc0000000000: 0000 [#1] PREEMPT SMP KASAN PTI
[   41.824488] KASAN: null-ptr-deref in range [0x0000000000000000-0x0000000000000007]
[   41.828027] RIP: 0010:buffer_queue+0xc2/0x500
[   41.836311] Call Trace:
[   41.836945]  __enqueue_in_driver+0x141/0x360
[   41.837262]  vb2_start_streaming+0x62/0x4a0
[   41.838216]  vb2_core_streamon+0x1da/0x2c0
[   41.838516]  __vb2_init_fileio+0x981/0xbc0
[   41.839141]  __vb2_perform_fileio+0xbf9/0x1120
[   41.840072]  vb2_fop_read+0x20e/0x400
[   41.840346]  v4l2_read+0x215/0x290
[   41.840603]  vfs_read+0x162/0x4c0

Fix this by checking the return value of cx88_risc_buffer()

[hverkuil: fix coding style issues]

## References
- https://git.kernel.org/stable/c/10c99d1c46ea9cd940029e17bab11d021f315c21
- https://git.kernel.org/stable/c/2b064d91440b33fba5b452f2d1b31f13ae911d71
- https://git.kernel.org/stable/c/4befc7ffa18ef9a4b70d854465313a345a06862f
- https://git.kernel.org/stable/c/644d5a87ab1863eb606526ea743021752a17e9cb
- https://git.kernel.org/stable/c/6f21976095c1e92454ab030976f95f40d652351b
- https://git.kernel.org/stable/c/704838040f3bdb4aa07ff4f26505a666a3defcfe
- https://git.kernel.org/stable/c/9181af2dbf06e7f432e5dbe88d10b22343e851b9
- https://git.kernel.org/stable/c/c2257c8a501537afab276c306cb717b7260276e1
- https://git.kernel.org/stable/c/c76d04d2079a4b7369ce9a0e859c0f3f2250bcc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50359.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50359
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
