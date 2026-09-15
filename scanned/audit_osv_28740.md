# [H] nouveau/uvmm: fix addr/range calcs for remap operations

## Summary
Severity: High
Advisory: CVE-2024-36018
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36018
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nouveau/uvmm: fix addr/range calcs for remap operations

dEQP-VK.sparse_resources.image_rebind.2d_array.r64i.128_128_8
was causing a remap operation like the below.

op_remap: prev: 0000003fffed0000 00000000000f0000 00000000a5abd18a 0000000000000000
op_remap: next:
op_remap: unmap: 0000003fffed0000 0000000000100000 0
op_map: map: 0000003ffffc0000 0000000000010000 000000005b1ba33c 00000000000e0000

This was resulting in an unmap operation from 0x3fffed0000+0xf0000, 0x100000
which was corrupting the pagetables and oopsing the kernel.

Fixes the prev + unmap range calcs to use start/end and map back to addr/range.

## References
- https://git.kernel.org/stable/c/0c16020d2b69a602c8ae6a1dd2aac9a3023249d6
- https://git.kernel.org/stable/c/692a51bebf4552bdf0a79ccd68d291182a26a569
- https://git.kernel.org/stable/c/be141849ec00ef39935bf169c0f194ac70bf85ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36018.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
