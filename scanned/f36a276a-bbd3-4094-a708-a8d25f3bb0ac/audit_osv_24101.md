# [H] bpf: fix potential 32-bit overflow when accessing ARRAY map element

## Summary
Severity: High
Advisory: CVE-2022-50167
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50167
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: fix potential 32-bit overflow when accessing ARRAY map element

If BPF array map is bigger than 4GB, element pointer calculation can
overflow because both index and elem_size are u32. Fix this everywhere
by forcing 64-bit multiplication. Extract this formula into separate
small helper and use it consistently in various places.

Speculative-preventing formula utilizing index_mask trick is left as is,
but explicit u64 casts are added in both places.

## References
- https://git.kernel.org/stable/c/063e092534d4c6785228e5b1eb6e9329f66ccbe4
- https://git.kernel.org/stable/c/3c7256b880b3a5aa1895fd169a34aa4224a11862
- https://git.kernel.org/stable/c/87ac0d600943994444e24382a87aa19acc4cd3d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50167.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50167
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
