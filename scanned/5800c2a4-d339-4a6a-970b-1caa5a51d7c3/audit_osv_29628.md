# [H] net/mlx5e: Take state lock during tx timeout reporter

## Summary
Severity: High
Advisory: CVE-2024-45019
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45019
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Take state lock during tx timeout reporter

mlx5e_safe_reopen_channels() requires the state lock taken. The
referenced changed in the Fixes tag removed the lock to fix another
issue. This patch adds it back but at a later point (when calling
mlx5e_safe_reopen_channels()) to avoid the deadlock referenced in the
Fixes tag.

## References
- https://git.kernel.org/stable/c/03d3734bd692affe4d0e9c9d638f491aaf37411b
- https://git.kernel.org/stable/c/8e57e66ecbdd2fddc9fbf3e984b1c523b70e9809
- https://git.kernel.org/stable/c/b3b9a87adee97854bcd71057901d46943076267e
- https://git.kernel.org/stable/c/e6b5afd30b99b43682a7764e1a74a42fe4d5f4b3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45019.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
