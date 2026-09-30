# [H] do_change_type(): refuse to operate on unmounted/not ours mounts

## Summary
Severity: High
Advisory: CVE-2025-38498
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-38498
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

do_change_type(): refuse to operate on unmounted/not ours mounts

Ensure that propagation settings can only be changed for mounts located
in the caller's mount namespace. This change aligns permission checking
with the rest of mount(2).

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://git.kernel.org/stable/c/064014f7812744451d5d0592f3d2bcd727f2ee93
- https://git.kernel.org/stable/c/12f147ddd6de7382dad54812e65f3f08d05809fc
- https://git.kernel.org/stable/c/19554c79a2095ddde850906a067915c1ef3a4114
- https://git.kernel.org/stable/c/432a171d60056489270c462e651e6c3a13f855b1
- https://git.kernel.org/stable/c/4f091ad0862b02dc42a19a120b7048de848561f8
- https://git.kernel.org/stable/c/787937c4e373f1722c4343e5a5a4eb0f8543e589
- https://git.kernel.org/stable/c/9c1ddfeb662b668fff69c5f1cfdd9f5d23d55d23
- https://git.kernel.org/stable/c/c7d11fdf8e5db5f34a6c062c7e6ba3a0971879d2
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38498.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38498
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
