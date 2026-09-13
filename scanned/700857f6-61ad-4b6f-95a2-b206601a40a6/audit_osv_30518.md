# [H] hv_sock: Initializing vsk->trans to NULL to prevent a dangling pointer

## Summary
Severity: High
Advisory: CVE-2024-53103
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53103
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8, >=6.12.0 <6.12.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

hv_sock: Initializing vsk->trans to NULL to prevent a dangling pointer

When hvs is released, there is a possibility that vsk->trans may not
be initialized to NULL, which could lead to a dangling pointer.
This issue is resolved by initializing vsk->trans to NULL.

## References
- https://git.kernel.org/stable/c/285266ef92f7b4bf7d26e1e95e215ce6a6badb4a
- https://git.kernel.org/stable/c/414476c4fb11be070c09ab8f3e75c9ee324a108a
- https://git.kernel.org/stable/c/4bdc5a62c6e50600d8a1c3e18fd6dce0c27c9497
- https://git.kernel.org/stable/c/4fe1d42f2acc463b733bb42e3f8e67dbc2a0eb2d
- https://git.kernel.org/stable/c/7cf25987820350cb950856c71b409e5b6eed52bd
- https://git.kernel.org/stable/c/8621725afb38e111969c64280b71480afde2aace
- https://git.kernel.org/stable/c/98d8dde9232250a57ad5ef16479bf6a349e09b80
- https://git.kernel.org/stable/c/e0fe3392371293175f25028020ded5267f4cd8e3
- https://git.kernel.org/stable/c/e629295bd60abf4da1db85b82819ca6a4f6c1e79
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53103.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53103
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
