# [H] drm/msm: Fix obj leak in VM_BIND error path

## Summary
Severity: High
Advisory: CVE-2025-40069
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40069
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix obj leak in VM_BIND error path

If we fail a handle-lookup part way thru, we need to drop the already
obtained obj references.

Patchwork: https://patchwork.freedesktop.org/patch/669784/

## References
- https://git.kernel.org/stable/c/278f8904434aa96055e793936b5977c010549e28
- https://git.kernel.org/stable/c/2b512909a291a964cfcf6b58de13256ab3e848c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40069.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
