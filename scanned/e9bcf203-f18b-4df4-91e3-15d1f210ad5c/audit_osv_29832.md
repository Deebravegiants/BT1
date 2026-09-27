# [H] drm/xe/client: add missing bo locking in show_meminfo()

## Summary
Severity: High
Advisory: CVE-2024-46866
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46866
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/client: add missing bo locking in show_meminfo()

bo_meminfo() wants to inspect bo state like tt and the ttm resource,
however this state can change at any point leading to stuff like NPD and
UAF, if the bo lock is not held. Grab the bo lock when calling
bo_meminfo(), ensuring we drop any spinlocks first. In the case of
object_idr we now also need to hold a ref.

v2 (MattB)
  - Also add xe_bo_assert_held()

(cherry picked from commit 4f63d712fa104c3ebefcb289d1e733e86d8698c7)

## References
- https://git.kernel.org/stable/c/94c4aa266111262c96c98f822d1bccc494786fee
- https://git.kernel.org/stable/c/abc8feacacf8fae10eecf6fea7865e8c1fee419c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46866.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46866
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
