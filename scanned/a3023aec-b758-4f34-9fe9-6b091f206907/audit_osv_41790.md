# [H] drm/amdgpu: fix amdgpu_hmm_range_get_pages

## Summary
Severity: High
Advisory: CVE-2026-63879
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63879
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix amdgpu_hmm_range_get_pages

The notifier sequence must only be read once or otherwise we could work
with invalid pages.

While at it also fix the coding style, e.g. drop the pre-initialized
return value and use the common define for 2G range.

(cherry picked from commit c08972f555945cda57b0adb72272a37910153390)

## References
- https://git.kernel.org/stable/c/2fd24407457a6b181ba827705678da70e528dcd0
- https://git.kernel.org/stable/c/962d684b5dc0741dcd93485d41b450de402d5592
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63879.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63879
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
