# [H] net/mlx5: Fix vport QoS cleanup on error

## Summary
Severity: High
Advisory: CVE-2025-21882
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21882
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Fix vport QoS cleanup on error

When enabling vport QoS fails, the scheduling node was never freed,
causing a leak.

Add the missing free and reset the vport scheduling node pointer to
NULL.

## References
- https://git.kernel.org/stable/c/7f3528f7d2f98b70e19a6bb7b130fc82c079ac54
- https://git.kernel.org/stable/c/fead368502bce0e10bea7c0d2895b2fa0c6c10aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21882.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21882
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
