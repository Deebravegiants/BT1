# [H] dma-buf: insert memory barrier before updating num_fences

## Summary
Severity: High
Advisory: CVE-2025-38095
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38095
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.241, >=5.11.0 <5.15.192, >=5.16.0 <6.1.140, >=6.2.0 <6.6.92, >=6.7.0 <6.12.30, >=6.13.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-buf: insert memory barrier before updating num_fences

smp_store_mb() inserts memory barrier after storing operation.
It is different with what the comment is originally aiming so Null
pointer dereference can be happened if memory update is reordered.

## References
- https://git.kernel.org/stable/c/08680c4dadc6e736c75bc2409d833f03f9003c51
- https://git.kernel.org/stable/c/3becc659f9cb76b481ad1fb71f54d5c8d6332d3f
- https://git.kernel.org/stable/c/72c7d62583ebce7baeb61acce6057c361f73be4a
- https://git.kernel.org/stable/c/90eb79c4ed98a4e24a62ccf61c199ab0f680fa8f
- https://git.kernel.org/stable/c/c9d2b9a80d06a58f37e0dc8c827075639b443927
- https://git.kernel.org/stable/c/d0b7f11dd68b593bd970e5735be00e8d89bace30
- https://git.kernel.org/stable/c/fe1bebd0edb22e3536cbc920ec713331d1367ad4
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38095.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
