# [H] drm/xe: Free job before xe_exec_queue_put

## Summary
Severity: High
Advisory: CVE-2024-44978
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44978
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Free job before xe_exec_queue_put

Free job depends on job->vm being valid, the last xe_exec_queue_put can
destroy the VM. Prevent UAF by freeing job before xe_exec_queue_put.

(cherry picked from commit 32a42c93b74c8ca6d0915ea3eba21bceff53042f)

## References
- https://git.kernel.org/stable/c/98aa0330f200b9b8fb9e1298e006eda57a13351c
- https://git.kernel.org/stable/c/9e7f30563677fbeff62d368d5d2a5ac7aaa9746a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44978.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44978
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
