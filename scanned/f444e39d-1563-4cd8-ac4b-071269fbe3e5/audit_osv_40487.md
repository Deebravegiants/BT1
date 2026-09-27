# [H] drm/i915/gem: Fix phys BO pread/pwrite with offset

## Summary
Severity: High
Advisory: CVE-2026-53356
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-53356
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/gem: Fix phys BO pread/pwrite with offset

sg_page() returns struct page pointer not (void *) so the scaling
of pread/pwrite is wrong for phys BO and wrong parts of BO would be
accessed if non-zero offset is used.

Last impacted platform with overlay or cursor planes using phys
mapping was Gen3/945G/Lakeport.

(cherry picked from commit 3e49a2f85070b2fb672c1e0fdba281a4ea3aebe6)

## References
- https://git.kernel.org/stable/c/07c33be968d9e0cab6cba38c81850a09942fcb2e
- https://git.kernel.org/stable/c/14469860e2e39b7095dcd658d2bad38a11110a68
- https://git.kernel.org/stable/c/1ec8fc63e9cdb22da54e48e536c9204020416fc6
- https://git.kernel.org/stable/c/32d4c5d328a3ff995420f4f85163e1e403f43628
- https://git.kernel.org/stable/c/3bd168dd835b93a3862cd05b0d13c432b115f9d6
- https://git.kernel.org/stable/c/40f738991058eb3e3530c3006a5bd6fd5e29f035
- https://git.kernel.org/stable/c/d21ad938398bca695a511307de38a65889e3b354
- https://git.kernel.org/stable/c/dd51a2eeb93bc6faa892ff9083911dd23f82c187
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53356.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
