# [H] drm/msm: Fix VM_BIND UNMAP locking

## Summary
Severity: High
Advisory: CVE-2026-53054
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53054
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix VM_BIND UNMAP locking

Wrong argument meant that the objs involved in UNMAP ops were not always
getting locked.

Since _NO_SHARE objs share a common resv with the VM (which is always
locked) this would only show up with non-_NO_SHARE BOs.

Patchwork: https://patchwork.freedesktop.org/patch/713898/

## References
- https://git.kernel.org/stable/c/206f812ef140727b75697111391ae320fd8aa652
- https://git.kernel.org/stable/c/85042c2cd970a6b0e686329387096fe19989ae62
- https://git.kernel.org/stable/c/d9ecf758270501b2e7a0bc1dd69a6f28f1ae3cae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53054.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53054
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
