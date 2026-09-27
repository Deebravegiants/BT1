# [H] media: pvrusb2: fix array-index-out-of-bounds in pvr2_i2c_core_init

## Summary
Severity: High
Advisory: CVE-2022-49478
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49478
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.18 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: pvrusb2: fix array-index-out-of-bounds in pvr2_i2c_core_init

Syzbot reported that -1 is used as array index. The problem was in
missing validation check.

hdw->unit_number is initialized with -1 and then if init table walk fails
this value remains unchanged. Since code blindly uses this member for
array indexing adding sanity check is the easiest fix for that.

hdw->workpoll initialization moved upper to prevent warning in
__flush_work.

## References
- https://git.kernel.org/stable/c/1310fc3538dcc375a2f46ef0a438512c2ca32827
- https://git.kernel.org/stable/c/24e807541e4a9263ed928e6ae3498de3ad43bd1e
- https://git.kernel.org/stable/c/2e004fe914b243db41fa96f9e583385f360ea58e
- https://git.kernel.org/stable/c/3309c2c574e13b21b44729f5bdbf21f60189b79a
- https://git.kernel.org/stable/c/4351bfe36aba9fa7dc9d68d498d25d41a0f45e67
- https://git.kernel.org/stable/c/471bec68457aaf981add77b4f590d65dd7da1059
- https://git.kernel.org/stable/c/a3304766d9384886e6d3092c776273526947a2e9
- https://git.kernel.org/stable/c/a3660e06675bccec4bf149c7229ea1d491ba10d7
- https://git.kernel.org/stable/c/f99a8b1ec0eddc2931aeaa4f490277a15b39f511
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49478.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
