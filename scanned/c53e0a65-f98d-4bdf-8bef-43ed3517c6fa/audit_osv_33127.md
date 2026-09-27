# [H] drm/xe/migrate: prevent potential UAF

## Summary
Severity: High
Advisory: CVE-2025-39740
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39740
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/migrate: prevent potential UAF

If we hit the error path, the previous fence (if there is one) has
already been put() prior to this, so doing a fence_wait could lead to
UAF. Tweak the flow to do to the put() until after we do the wait.

(cherry picked from commit 9b7ca35ed28fe5fad86e9d9c24ebd1271e4c9c3e)

## References
- https://git.kernel.org/stable/c/145832fbdd17b1d77ffd6cdd1642259e101d1b7e
- https://git.kernel.org/stable/c/7e46fa64a4b94208563c3a5bf1d7f4346f94abea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39740.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39740
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
