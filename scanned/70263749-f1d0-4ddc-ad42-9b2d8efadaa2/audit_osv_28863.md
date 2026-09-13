# [H] nilfs2: fix potential kernel bug due to lack of writeback flag waiting

## Summary
Severity: High
Advisory: CVE-2024-37078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-37078
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix potential kernel bug due to lack of writeback flag waiting

Destructive writes to a block device on which nilfs2 is mounted can cause
a kernel bug in the folio/page writeback start routine or writeback end
routine (__folio_start_writeback in the log below):

 kernel BUG at mm/page-writeback.c:3070!
 Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI
 ...
 RIP: 0010:__folio_start_writeback+0xbaa/0x10e0
 Code: 25 ff 0f 00 00 0f 84 18 01 00 00 e8 40 ca c6 ff e9 17 f6 ff ff
  e8 36 ca c6 ff 4c 89 f7 48 c7 c6 80 c0 12 84 e8 e7 b3 0f 00 90 <0f>
  0b e8 1f ca c6 ff 4c 89 f7 48 c7 c6 a0 c6 12 84 e8 d0 b3 0f 00
 ...
 Call Trace:
  <TASK>
  nilfs_segctor_do_construct+0x4654/0x69d0 [nilfs2]
  nilfs_segctor_construct+0x181/0x6b0 [nilfs2]
  nilfs_segctor_thread+0x548/0x11c0 [nilfs2]
  kthread+0x2f0/0x390
  ret_from_fork+0x4b/0x80
  ret_from_fork_asm+0x1a/0x30
  </TASK>

This is because when the log writer starts a writeback for segment summary
blocks or a super root block that use the backing device's page cache, it
does not wait for the ongoing folio/page writeback, resulting in an
inconsistent writeback state.

Fix this issue by waiting for ongoing writebacks when putting
folios/pages on the backing device into writeback state.

## References
- https://git.kernel.org/stable/c/0ecfe3a92869a59668d27228dabbd7965e83567f
- https://git.kernel.org/stable/c/1f3bff69f1214fe03a02bc650d5bbfaa6e65ae7d
- https://git.kernel.org/stable/c/271dcd977ccda8c7a26e360425ae7b4db7d2ecc0
- https://git.kernel.org/stable/c/33900d7eae616647e179eee1c66ebe654ee39627
- https://git.kernel.org/stable/c/614d397be0cf43412b3f94a0f6460eddced8ce92
- https://git.kernel.org/stable/c/95f6f81e50d858a7c9aa7c795ec14a0ac3819118
- https://git.kernel.org/stable/c/a4ca369ca221bb7e06c725792ac107f0e48e82e7
- https://git.kernel.org/stable/c/a75b8f493dfc48aa38c518430bd9e03b53bffebe
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37078.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
