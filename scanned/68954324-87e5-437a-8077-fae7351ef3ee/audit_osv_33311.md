# [H] crypto: comp - Use same definition of context alloc and free ops

## Summary
Severity: High
Advisory: CVE-2025-40063
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40063
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: comp - Use same definition of context alloc and free ops

In commit 42d9f6c77479 ("crypto: acomp - Move scomp stream allocation
code into acomp"), the crypto_acomp_streams struct was made to rely on
having the alloc_ctx and free_ctx operations defined in the same order
as the scomp_alg struct. But in that same commit, the alloc_ctx and
free_ctx members of scomp_alg may be randomized by structure layout
randomization, since they are contained in a pure ops structure
(containing only function pointers). If the pointers within scomp_alg
are randomized, but those in crypto_acomp_streams are not, then
the order may no longer match. This fixes the problem by removing the
union from scomp_alg so that both crypto_acomp_streams and scomp_alg
will share the same definition of alloc_ctx and free_ctx, ensuring
they will always have the same layout.

## References
- https://git.kernel.org/stable/c/779d3b6f2d32c5f1da6163e959abe1e1ffe2945b
- https://git.kernel.org/stable/c/f75f66683ded09f7135aef2e763c245a07c8271a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40063.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40063
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
