# [M] drm/amd/display: Fix 'panel_cntl' could be null in 'dcn21_set_backlight_level()'

## Summary
Severity: Medium
Advisory: CVE-2024-26662
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26662
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix 'panel_cntl' could be null in 'dcn21_set_backlight_level()'

'panel_cntl' structure used to control the display panel could be null,
dereferencing it could lead to a null pointer access.

Fixes the below:
drivers/gpu/drm/amd/amdgpu/../display/dc/hwss/dcn21/dcn21_hwseq.c:269 dcn21_set_backlight_level() error: we previously assumed 'panel_cntl' could be null (see line 250)

## References
- https://git.kernel.org/stable/c/0c863cab0e9173f8b6c7bc328bee3b8625f131b5
- https://git.kernel.org/stable/c/2e150ccea13129eb048679114808eb9770443e4d
- https://git.kernel.org/stable/c/e96fddb32931d007db12b1fce9b5e8e4c080401b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26662.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
