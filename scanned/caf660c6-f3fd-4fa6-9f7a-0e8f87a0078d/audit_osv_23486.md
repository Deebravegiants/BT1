# [H] media: vivid: fix compose size exceed boundary

## Summary
Severity: High
Advisory: CVE-2022-48945
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-23
Source: https://osv.dev/vulnerability/CVE-2022-48945
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vivid: fix compose size exceed boundary

syzkaller found a bug:

 BUG: unable to handle page fault for address: ffffc9000a3b1000
 #PF: supervisor write access in kernel mode
 #PF: error_code(0x0002) - not-present page
 PGD 100000067 P4D 100000067 PUD 10015f067 PMD 1121ca067 PTE 0
 Oops: 0002 [#1] PREEMPT SMP
 CPU: 0 PID: 23489 Comm: vivid-000-vid-c Not tainted 6.1.0-rc1+ #512
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1ubuntu1.1 04/01/2014
 RIP: 0010:memcpy_erms+0x6/0x10
[...]
 Call Trace:
  <TASK>
  ? tpg_fill_plane_buffer+0x856/0x15b0
  vivid_fillbuff+0x8ac/0x1110
  vivid_thread_vid_cap_tick+0x361/0xc90
  vivid_thread_vid_cap+0x21a/0x3a0
  kthread+0x143/0x180
  ret_from_fork+0x1f/0x30
  </TASK>

This is because we forget to check boundary after adjust compose->height
int V4L2_SEL_TGT_CROP case. Add v4l2_rect_map_inside() to fix this problem
for this case.

## References
- https://git.kernel.org/stable/c/2f558c5208b0f70c8140e08ce09fcc84da48e789
- https://git.kernel.org/stable/c/54f259906039dbfe46c550011409fa16f72370f6
- https://git.kernel.org/stable/c/5edc3604151919da8da0fb092b71d7dce07d848a
- https://git.kernel.org/stable/c/8c0ee15d9a102c732d0745566d254040085d5663
- https://git.kernel.org/stable/c/94a7ad9283464b75b12516c5512541d467cefcf8
- https://git.kernel.org/stable/c/9c7fba9503b826f0c061d136f8f0c9f953ed18b9
- https://git.kernel.org/stable/c/ab54081a2843aefb837812fac5488cc8f1696142
- https://git.kernel.org/stable/c/ccb5392c4fea0e7d9f7ab35567e839d74cb3998b
- https://git.kernel.org/stable/c/f9d19f3a044ca651b0be52a4bf951ffe74259b9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48945.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
