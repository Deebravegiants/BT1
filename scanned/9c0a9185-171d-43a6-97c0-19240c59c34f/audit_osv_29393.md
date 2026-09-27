# [H] drm/i915/gem: Fix Virtual Memory mapping boundaries calculation

## Summary
Severity: High
Advisory: CVE-2024-42259
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-14
Source: https://osv.dev/vulnerability/CVE-2024-42259
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.106, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/gem: Fix Virtual Memory mapping boundaries calculation

Calculating the size of the mapped area as the lesser value
between the requested size and the actual size does not consider
the partial mapping offset. This can cause page fault access.

Fix the calculation of the starting and ending addresses, the
total size is now deduced from the difference between the end and
start addresses.

Additionally, the calculations have been rewritten in a clearer
and more understandable form.

[Joonas: Add Requires: tag]
Requires: 60a2066c5005 ("drm/i915/gem: Adjust vma offset for framebuffer mmap offset")
(cherry picked from commit 97b6784753da06d9d40232328efc5c5367e53417)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3e06073d24807f04b4694108a8474decb7b99e60
- https://git.kernel.org/stable/c/4b09513ce93b3dcb590baaaff2ce96f2d098312d
- https://git.kernel.org/stable/c/50111a8098fb9ade621eeff82228a997d42732ab
- https://git.kernel.org/stable/c/8bdd9ef7e9b1b2a73e394712b72b22055e0e26c3
- https://git.kernel.org/stable/c/911f8055f175c82775d0fd8cedcd0b75413f4ba7
- https://git.kernel.org/stable/c/a256d019eaf044864c7e50312f0a65b323c24f39
- https://git.kernel.org/stable/c/e8a68aa842d3f8dd04a46b9d632e5f67fde1da9b
- https://git.kernel.org/stable/c/ead9289a51ea82eb5b27029fcf4c34b2dd60cf06
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://project-zero.issues.chromium.org/issues/42451707
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42259.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42259
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
