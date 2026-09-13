# [H] drm/xe: Use local fence in error path of xe_migrate_clear

## Summary
Severity: High
Advisory: CVE-2025-37869
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37869
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Use local fence in error path of xe_migrate_clear

The intent of the error path in xe_migrate_clear is to wait on locally
generated fence and then return. The code is waiting on m->fence which
could be the local fence but this is only stable under the job mutex
leading to a possible UAF. Fix code to wait on local fence.

(cherry picked from commit 762b7e95362170b3e13a8704f38d5e47eca4ba74)

## References
- https://git.kernel.org/stable/c/20659d3150f1a2a258a173fe011013178ff2a197
- https://git.kernel.org/stable/c/2ac5f466f62892a7d1ac2d1a3eb6cd14efbe2f2d
- https://git.kernel.org/stable/c/dc712938aa26b001f448d5e93f59d57fa80f2dbd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37869.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37869
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
