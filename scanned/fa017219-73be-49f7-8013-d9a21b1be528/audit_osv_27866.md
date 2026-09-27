# [M] drm/amd/display: Fix variable deferencing before NULL check in edp_setup_replay()

## Summary
Severity: Medium
Advisory: CVE-2024-26648
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-26648
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix variable deferencing before NULL check in edp_setup_replay()

In edp_setup_replay(), 'struct dc *dc' & 'struct dmub_replay *replay'
was dereferenced before the pointer 'link' & 'replay' NULL check.

Fixes the below:
drivers/gpu/drm/amd/amdgpu/../display/dc/link/protocols/link_edp_panel_control.c:947 edp_setup_replay() warn: variable dereferenced before check 'link' (see line 933)

## References
- https://git.kernel.org/stable/c/22ae604aea14756954e1c00ae653e34d2afd2935
- https://git.kernel.org/stable/c/7073934f5d73f8b53308963cee36f0d389ea857c
- https://git.kernel.org/stable/c/c02d257c654191ecda1dc1af6875d527e85310e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26648.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26648
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
