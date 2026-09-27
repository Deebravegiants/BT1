# [H] drm/panthor: Fix UAF on kernel BO VA nodes

## Summary
Severity: High
Advisory: CVE-2025-68747
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68747
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Fix UAF on kernel BO VA nodes

If the MMU is down, panthor_vm_unmap_range() might return an error.
We expect the page table to be updated still, and if the MMU is blocked,
the rest of the GPU should be blocked too, so no risk of accessing
physical memory returned to the system (which the current code doesn't
cover for anyway).

Proceed with the rest of the cleanup instead of bailing out and leaving
the va_node inserted in the drm_mm, which leads to UAF when other
adjacent nodes are removed from the drm_mm tree.

## References
- https://git.kernel.org/stable/c/0612704b6f6ddf2ae223019c52148c5ac76cf70e
- https://git.kernel.org/stable/c/1123eadb843588b361c96f53a771202b7953154f
- https://git.kernel.org/stable/c/5a0060ddfc1fcfdb0f7b4fa1b7b3b0c436151391
- https://git.kernel.org/stable/c/98dd5143447af0ee33551776d8b2560c35d0bc4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68747.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
