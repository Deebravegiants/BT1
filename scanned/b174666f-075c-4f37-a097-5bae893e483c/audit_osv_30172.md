# [M] drm/xe: fix unbalanced rpm put() with fence_fini()

## Summary
Severity: Medium
Advisory: CVE-2024-50144
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50144
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: fix unbalanced rpm put() with fence_fini()

Currently we can call fence_fini() twice if something goes wrong when
sending the GuC CT for the tlb request, since we signal the fence and
return an error, leading to the caller also calling fini() on the error
path in the case of stack version of the flow, which leads to an extra
rpm put() which might later cause device to enter suspend when it
shouldn't. It looks like we can just drop the fini() call since the
fence signaller side will already call this for us.

There are known mysterious splats with device going to sleep even with
an rpm ref, and this could be one candidate.

v2 (Matt B):
  - Prefer warning if we detect double fini()

(cherry picked from commit cfcbc0520d5055825f0647ab922b655688605183)

## References
- https://git.kernel.org/stable/c/03a86c24aea0920a1ca20a0d7771d5e176db538d
- https://git.kernel.org/stable/c/046bd018c0123b1a49c22abed5f9ea31d1454c78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50144.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50144
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
