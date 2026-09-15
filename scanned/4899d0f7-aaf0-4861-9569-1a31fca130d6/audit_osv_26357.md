# [H] drm/i915: Avoid potential vm use-after-free

## Summary
Severity: High
Advisory: CVE-2023-52931
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52931
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Avoid potential vm use-after-free

Adding the vm to the vm_xa table makes it visible to userspace, which
could try to race with us to close the vm.  So we need to take our extra
reference before putting it in the table.

(cherry picked from commit 99343c46d4e2b34c285d3d5f68ff04274c2f9fb4)

## References
- https://git.kernel.org/stable/c/41d419382ec7e257e54b7b6ff0d3623aafb1316d
- https://git.kernel.org/stable/c/764accc2c1b8fd1507be2e7f436c94cdce887a00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52931.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52931
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
