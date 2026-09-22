# [H] drm/xe/ufence: Prefetch ufence addr to catch bogus address

## Summary
Severity: High
Advisory: CVE-2024-53098
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-53098
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/ufence: Prefetch ufence addr to catch bogus address

access_ok() only checks for addr overflow so also try to read the addr
to catch invalid addr sent from userspace.

(cherry picked from commit 9408c4508483ffc60811e910a93d6425b8e63928)

## References
- https://git.kernel.org/stable/c/5d623ffbae96b23f1fc43a3d5a267aabdb07583d
- https://git.kernel.org/stable/c/9c1813b3253480b30604c680026c7dc721ce86d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53098.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53098
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
