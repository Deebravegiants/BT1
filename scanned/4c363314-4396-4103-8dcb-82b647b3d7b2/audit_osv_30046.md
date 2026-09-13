# [H] drm/xe/vm: move xa_alloc to prevent UAF

## Summary
Severity: High
Advisory: CVE-2024-49865
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49865
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/vm: move xa_alloc to prevent UAF

Evil user can guess the next id of the vm before the ioctl completes and
then call vm destroy ioctl to trigger UAF since create ioctl is still
referencing the same vm. Move the xa_alloc all the way to the end to
prevent this.

v2:
 - Rebase

(cherry picked from commit dcfd3971327f3ee92765154baebbaece833d3ca9)

## References
- https://git.kernel.org/stable/c/09cf8901fc0225898311b375cfcc67bae37ed5da
- https://git.kernel.org/stable/c/74231870cf4976f69e83aa24f48edb16619f652f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49865.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
