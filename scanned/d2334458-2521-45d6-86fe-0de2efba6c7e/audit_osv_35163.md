# [H] accel/ivpu: Fix race condition when unbinding BOs

## Summary
Severity: High
Advisory: CVE-2025-68749
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68749
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.68, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Fix race condition when unbinding BOs

Fix 'Memory manager not clean during takedown' warning that occurs
when ivpu_gem_bo_free() removes the BO from the BOs list before it
gets unmapped. Then file_priv_unbind() triggers a warning in
drm_mm_takedown() during context teardown.

Protect the unmapping sequence with bo_list_lock to ensure the BO is
always fully unmapped when removed from the list. This ensures the BO
is either fully unmapped at context teardown time or present on the
list and unmapped by file_priv_unbind().

## References
- https://git.kernel.org/stable/c/00812636df370bedf4e44a0c81b86ea96bca8628
- https://git.kernel.org/stable/c/0328bb097bef05a796217c54b3d651cc3782827c
- https://git.kernel.org/stable/c/d71333ffdd3707d84cfb95acfaf8ba892adc066b
- https://git.kernel.org/stable/c/fb16493ebd8f171bcf0772262619618a131f30f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68749.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68749
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
