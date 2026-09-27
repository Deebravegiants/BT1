# [H] media: camss: Clean up received buffers on failed start of streaming

## Summary
Severity: High
Advisory: CVE-2022-50757
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50757
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: camss: Clean up received buffers on failed start of streaming

It is required to return the received buffers, if streaming can not be
started. For instance media_pipeline_start() may fail with EPIPE, if
a link validation between entities is not passed, and in such a case
a user gets a kernel warning:

  WARNING: CPU: 1 PID: 520 at drivers/media/common/videobuf2/videobuf2-core.c:1592 vb2_start_streaming+0xec/0x160
  <snip>
  Call trace:
   vb2_start_streaming+0xec/0x160
   vb2_core_streamon+0x9c/0x1a0
   vb2_ioctl_streamon+0x68/0xbc
   v4l_streamon+0x30/0x3c
   __video_do_ioctl+0x184/0x3e0
   video_usercopy+0x37c/0x7b0
   video_ioctl2+0x24/0x40
   v4l2_ioctl+0x4c/0x70

The fix is to correct the error path in video_start_streaming() of camss.

## References
- https://git.kernel.org/stable/c/04c734c716a97f1493b1edac41316aaed1d2a9d9
- https://git.kernel.org/stable/c/24df4fa3e795fb4b15fd4d3c036596e0978d265a
- https://git.kernel.org/stable/c/3d5cab726e3b370fea1b6e67183f0e13c409ce5c
- https://git.kernel.org/stable/c/75954cde8a5ca84003b24b6bf83197240935bd74
- https://git.kernel.org/stable/c/c8f3582345e6a69da65ab588f7c4c2d1685b0e80
- https://git.kernel.org/stable/c/d1c44928bb3ca0ec88e7ad5937a2a26a259aede6
- https://git.kernel.org/stable/c/f05326a440dc31b91b688b2f3f15b7347894a50b
- https://git.kernel.org/stable/c/fe443b3fe36cd23d4f5dc6d825d34322e7c89f0c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50757.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50757
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
