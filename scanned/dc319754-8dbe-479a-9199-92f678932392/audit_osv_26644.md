# [M] drm/ttm: fix bulk_move corruption when adding a entry

## Summary
Severity: Medium
Advisory: CVE-2023-53444
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53444
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/ttm: fix bulk_move corruption when adding a entry

When the resource is the first in the bulk_move range, adding it again
(thus moving it to the tail) will corrupt the list since the first
pointer is not moved. This eventually lead to null pointer deref in
ttm_lru_bulk_move_del()

## References
- https://git.kernel.org/stable/c/4481913607e58196c48a4fef5e6f45350684ec3c
- https://git.kernel.org/stable/c/70a3015683b007a0db4a1e858791b69afd45fc83
- https://git.kernel.org/stable/c/e7cf50e41bdc2d574056ebbfeaafc5f0e2562d5b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53444.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53444
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
