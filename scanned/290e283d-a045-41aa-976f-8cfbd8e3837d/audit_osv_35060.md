# [H] gpiolib: fix invalid pointer access in debugfs

## Summary
Severity: High
Advisory: CVE-2025-68167
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68167
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpiolib: fix invalid pointer access in debugfs

If the memory allocation in gpiolib_seq_start() fails, the s->private
field remains uninitialized and is later dereferenced without checking
in gpiolib_seq_stop(). Initialize s->private to NULL before calling
kzalloc() and check it before dereferencing it.

## References
- https://git.kernel.org/stable/c/2f6115ad8864cf3f48598f26c74c7c8e5c391919
- https://git.kernel.org/stable/c/3c91c8f424d3e44c8645ab765a38773e58afb07d
- https://git.kernel.org/stable/c/70180a6031056096c93ed2f47c41803268bdd91c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68167.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68167
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
