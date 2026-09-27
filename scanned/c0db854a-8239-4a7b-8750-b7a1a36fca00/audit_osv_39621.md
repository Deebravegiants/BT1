# [H] drm/amdgpu/userq: fix access to stale wptr mapping

## Summary
Severity: High
Advisory: CVE-2026-46311
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46311
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/userq: fix access to stale wptr mapping

Use drm_exec to take both locks i.e vm root bo and
wptr_obj bo to access the mapping data properly.

This fixes the security issue of unmap the wptr_obj while
a queue creation is in progress and passing other
bo at same address.

(cherry picked from commit 1fc6c8ab45dbee096469c08c13f6099d57a52d6c)

## References
- https://git.kernel.org/stable/c/336a9186f3a4b65bbd865d93936605ac8a1a3991
- https://git.kernel.org/stable/c/6da7b1242da4455b11c24ce667d1cab1a348c8ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46311.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46311
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
