# [H] ksmbd: add bounds check for create lease context

## Summary
Severity: High
Advisory: CVE-2025-22042
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22042
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add bounds check for create lease context

Add missing bounds check for create lease context.

## References
- https://git.kernel.org/stable/c/60b7207893a8a06c78441934931a08fdad63f18e
- https://git.kernel.org/stable/c/629dd37acc336ad778979361c351e782053ea284
- https://git.kernel.org/stable/c/800c482c9ef5910f05e3a713943c67cc6c1d4939
- https://git.kernel.org/stable/c/9a1b6ea955e6c7b29939a6d98701202f9d9644ec
- https://git.kernel.org/stable/c/a41cd52f00907a040ca22c73d4805bb79b0d0972
- https://git.kernel.org/stable/c/bab703ed8472aa9d109c5f8c1863921533363dae
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22042.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22042
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
