# [H] bpf: Propagate error from htab_lock_bucket() to userspace

## Summary
Severity: High
Advisory: CVE-2022-50490
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2022-50490
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Propagate error from htab_lock_bucket() to userspace

In __htab_map_lookup_and_delete_batch() if htab_lock_bucket() returns
-EBUSY, it will go to next bucket. Going to next bucket may not only
skip the elements in current bucket silently, but also incur
out-of-bound memory access or expose kernel memory to userspace if
current bucket_cnt is greater than bucket_size or zero.

Fixing it by stopping batch operation and returning -EBUSY when
htab_lock_bucket() fails, and the application can retry or skip the busy
batch as needed.

## References
- https://git.kernel.org/stable/c/0e13425104903970a5ede853082d3bbb4edec6f3
- https://git.kernel.org/stable/c/4f1f39a8f1ce1b24fee6852d7dcd704ce7c4334d
- https://git.kernel.org/stable/c/66a7a92e4d0d091e79148a4c6ec15d1da65f4280
- https://git.kernel.org/stable/c/6bfee6eb3d6b96ae730a542909dd22b5f9f50d58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50490.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
