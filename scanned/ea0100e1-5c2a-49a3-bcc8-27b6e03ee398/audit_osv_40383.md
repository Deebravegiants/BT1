# [H] bpf: Fix OOB in pcpu_init_value

## Summary
Severity: High
Advisory: CVE-2026-53076
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53076
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix OOB in pcpu_init_value

An out-of-bounds read occurs when copying element from a
BPF_MAP_TYPE_CGROUP_STORAGE map to another pcpu map with the
same value_size that is not rounded up to 8 bytes.

The issue happens when:
1. A CGROUP_STORAGE map is created with value_size not aligned to
   8 bytes (e.g., 4 bytes)
2. A pcpu map is created with the same value_size (e.g., 4 bytes)
3. Update element in 2 with data in 1

pcpu_init_value assumes that all sources are rounded up to 8 bytes,
and invokes copy_map_value_long to make a data copy, However, the
assumption doesn't stand since there are some cases where the source
may not be rounded up to 8 bytes, e.g., CGROUP_STORAGE, skb->data.
the verifier verifies exactly the size that the source claims, not
the size rounded up to 8 bytes by kernel, an OOB happens when the
source has only 4 bytes while the copy size(4) is rounded up to 8.

## References
- https://git.kernel.org/stable/c/576afddfee8d1108ee299bf10f581593540d1a36
- https://git.kernel.org/stable/c/6086079e6d1c32ba4c4b422612b8aebb1129a96c
- https://git.kernel.org/stable/c/634a793d0e1c822412095d25a1338f8831ad894c
- https://git.kernel.org/stable/c/e0378419b0e20178b5d100b27c9cc7e51064202e
- https://git.kernel.org/stable/c/e19c5ed9f1922a6854073f8651a63fa7be26e9e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53076.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
