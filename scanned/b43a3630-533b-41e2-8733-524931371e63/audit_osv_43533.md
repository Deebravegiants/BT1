# [H] configfs: fix lockless traversals of ->s_children

## Summary
Severity: High
Advisory: CVE-2026-74330
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74330
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

configfs: fix lockless traversals of ->s_children

Having the parent directory locked protects entries from removal
by another thread, but it does *not* protect cursors from being
moved around by lseek() - or freed, for that matter.

## References
- https://git.kernel.org/stable/c/459860529c109c5ce08b81c0776ca1200eaaeb4a
- https://git.kernel.org/stable/c/637ef4961470e04455102b34ac484a34d8eca0a4
- https://git.kernel.org/stable/c/77fd6f50f633a52c2db061e7d71d8cb486b0265e
- https://git.kernel.org/stable/c/91f289728ec706b7ff1ca0ee845dd73ff2253488
- https://git.kernel.org/stable/c/9b9e8bb81c41fd27e7b57a1c936fde140548535f
- https://git.kernel.org/stable/c/9e57e2863872e82e7c7237bc32299f67ebebc543
- https://git.kernel.org/stable/c/b166ab78dc3f48e83d2c80bdfde4159b31fdc5fb
- https://git.kernel.org/stable/c/e6d93108e0a27d7e6f95c7e45017d14ba2900d32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74330.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74330
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
