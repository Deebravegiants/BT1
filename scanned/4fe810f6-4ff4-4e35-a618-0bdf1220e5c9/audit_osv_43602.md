# [H] drm/panthor: reject firmware sections with oversized data

## Summary
Severity: High
Advisory: CVE-2026-74452
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74452
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: reject firmware sections with oversized data

In panthor_fw_load_section_entry(), the data size to copy is calculated
without validating it against the allocated section_size:

    section->data.size = hdr.data.end - hdr.data.start;

If a crafted firmware sets data.size larger than the allocated memory,
this could cause a heap buffer overflow in panthor_fw_init_section_mem()

    memcpy(section->mem->kmap, section->data.buf, section->data.size);

Additionally, if the section->data.size exceeds the BO size, could this
memset underflow the size calculation, leading to a massive out-of-bounds
zeroing of kernel memory?

    memset(section->mem->kmap + section->data.size, 0,
           panthor_kernel_bo_size(section->mem) - section->data.size);

Reject section entries whose initial data is larger than the section size.

## References
- https://git.kernel.org/stable/c/0e57165ca025a67d8dfd17efd2765fdd4925fdab
- https://git.kernel.org/stable/c/2a761b9be5863e1d26a584f0c2d1e114a684ed9a
- https://git.kernel.org/stable/c/7f4674d986c15c74327cb6ac6e2e2afecf061e04
- https://git.kernel.org/stable/c/a3caaa06809248b996254be5b47e10804a3494e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74452
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
