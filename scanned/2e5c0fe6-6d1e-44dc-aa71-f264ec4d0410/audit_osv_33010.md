# [H] net: appletalk: Fix device refcount leak in atrtr_create()

## Summary
Severity: High
Advisory: CVE-2025-38542
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38542
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.189, >=5.16.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: appletalk: Fix device refcount leak in atrtr_create()

When updating an existing route entry in atrtr_create(), the old device
reference was not being released before assigning the new device,
leading to a device refcount leak. Fix this by calling dev_put() to
release the old device reference before holding the new one.

## References
- https://git.kernel.org/stable/c/473f3eadfc73b0fb6d8dee5829d19a5772e387f7
- https://git.kernel.org/stable/c/4a17370da6e476d3d275534e9e9cd2d02c57ca46
- https://git.kernel.org/stable/c/64124cf0aab0dd1e18c0fb5ae66e45741e727f8b
- https://git.kernel.org/stable/c/711c80f7d8b163d3ecd463cd96f07230f488e750
- https://git.kernel.org/stable/c/a7852b01793669248dce0348d14df89e77a32afd
- https://git.kernel.org/stable/c/b2f5dfa87367fdce9f8b995bc6c38f64f9ea2c90
- https://git.kernel.org/stable/c/b92bedf71f25303e203a4e657489d76691a58119
- https://git.kernel.org/stable/c/d2e9f50f0bdad73b64a871f25186b899624518c4
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38542.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38542
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
