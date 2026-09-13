# [H] drm/amdkfd: don't allow mapping the MMIO HDP page with large pages

## Summary
Severity: High
Advisory: CVE-2024-41011
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/CVE-2024-41011
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: don't allow mapping the MMIO HDP page with large pages

We don't get the right offset in that case.  The GPU has
an unused 4K area of the register BAR space into which you can
remap registers.  We remap the HDP flush registers into this
space to allow userspace (CPU or GPU) to flush the HDP when it
updates VRAM.  However, on systems with >4K pages, we end up
exposing PAGE_SIZE of MMIO space.

## References
- https://git.kernel.org/stable/c/009c4d78bcf07c4ac2e3dd9f275b4eaa72b4f884
- https://git.kernel.org/stable/c/4b4cff994a27ebf7bd3fb9a798a1cdfa8d01b724
- https://git.kernel.org/stable/c/6186c93560889265bfe0914609c274eff40bbeb5
- https://git.kernel.org/stable/c/89fffbdf535ce659c1a26b51ad62070566e33b28
- https://git.kernel.org/stable/c/8ad4838040e5515939c071a0f511ce2661a0889d
- https://git.kernel.org/stable/c/be4a2a81b6b90d1a47eaeaace4cc8e2cb57b96c7
- https://git.kernel.org/stable/c/f7276cdc1912325b64c33fcb1361952c06e55f63
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41011.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
