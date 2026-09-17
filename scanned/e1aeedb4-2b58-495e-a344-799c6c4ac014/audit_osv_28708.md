# [H] drm/panfrost: Fix the error path in panfrost_mmu_map_fault_addr()

## Summary
Severity: High
Advisory: CVE-2024-35951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35951
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panfrost: Fix the error path in panfrost_mmu_map_fault_addr()

Subject: [PATCH] drm/panfrost: Fix the error path in
 panfrost_mmu_map_fault_addr()

If some the pages or sgt allocation failed, we shouldn't release the
pages ref we got earlier, otherwise we will end up with unbalanced
get/put_pages() calls. We should instead leave everything in place
and let the BO release function deal with extra cleanup when the object
is destroyed, or let the fault handler try again next time it's called.

## References
- http://www.openwall.com/lists/oss-security/2024/05/30/1
- http://www.openwall.com/lists/oss-security/2024/05/30/2
- https://git.kernel.org/stable/c/1fc9af813b25e146d3607669247d0f970f5a87c3
- https://git.kernel.org/stable/c/31806711e8a4b75e09b1c43652f2a6420e6e1002
- https://git.kernel.org/stable/c/e18070c622c63f0cab170348e320454728c277aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35951.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
