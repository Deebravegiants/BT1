# [H] media: chips-media: wave5: Fix Null reference while testing fluster

## Summary
Severity: High
Advisory: CVE-2026-43263
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43263
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: chips-media: wave5: Fix Null reference while testing fluster

When multi instances are created/destroyed, many interrupts happens
and structures for decoder are removed.
"struct vpu_instance" this structure is shared for all flow in the decoder,
so if the structure is not protected by lock, Null dereference
could happens sometimes.
IRQ Handler was spilt to two phases and Lock was added as well.

## References
- https://git.kernel.org/stable/c/d12bcf183ec7da4305d848068d15f18044eaf62a
- https://git.kernel.org/stable/c/e66ff2b08e4ee1c4d3b84f24818e5bcc178cc3a4
- https://git.kernel.org/stable/c/ea316b784fe6a61b29131c98cddb24e651b1dcbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43263.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43263
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
