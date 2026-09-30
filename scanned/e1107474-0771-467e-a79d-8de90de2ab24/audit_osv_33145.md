# [H] NFS: Fix the setting of capabilities when automounting a new filesystem

## Summary
Severity: High
Advisory: CVE-2025-39798
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/CVE-2025-39798
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix the setting of capabilities when automounting a new filesystem

Capabilities cannot be inherited when we cross into a new filesystem.
They need to be reset to the minimal defaults, and then probed for
again.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/175afda783e38c0660f2afc0602dd9c83d4e7ee1
- https://git.kernel.org/stable/c/3924dab90816d0c683a110628ef386f83a9d1e13
- https://git.kernel.org/stable/c/50e0fd0050e510e749e1fdd1d7158e419ff8f3b9
- https://git.kernel.org/stable/c/73fcb101bb3eb2a552d7856a476b2c0bc3b5ef9e
- https://git.kernel.org/stable/c/816a6f60c2c2b679a33fa4276442bafd11473651
- https://git.kernel.org/stable/c/95eb0d97ab98a10e966125c1f274e7d0fc0992b3
- https://git.kernel.org/stable/c/987c20428f067c1c7f29ed0a2bd8c63fa74b1c2c
- https://git.kernel.org/stable/c/a8ffee4abd8ec9d7a64d394e0306ae64ba139fd2
- https://git.kernel.org/stable/c/b01f21cacde9f2878492cf318fee61bf4ccad323
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39798.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39798
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
