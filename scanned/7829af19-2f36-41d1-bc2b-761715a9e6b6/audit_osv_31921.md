# [M] drm/amd/display: fix missing .is_two_pixels_per_container

## Summary
Severity: Medium
Advisory: CVE-2025-21989
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-21989
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: fix missing .is_two_pixels_per_container

Starting from 6.11, AMDGPU driver, while being loaded with amdgpu.dc=1,
due to lack of .is_two_pixels_per_container function in dce60_tg_funcs,
causes a NULL pointer dereference on PCs with old GPUs, such as R9 280X.

So this fix adds missing .is_two_pixels_per_container to dce60_tg_funcs.

(cherry picked from commit bd4b125eb949785c6f8a53b0494e32795421209d)

## References
- https://git.kernel.org/stable/c/36d04c9313d8d83ead92242f037099ac73e02120
- https://git.kernel.org/stable/c/e204aab79e01bc8ff750645666993ed8b719de57
- https://git.kernel.org/stable/c/fefa811e616b5d0b555ed65743e528a0a8a0b377
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21989.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21989
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
