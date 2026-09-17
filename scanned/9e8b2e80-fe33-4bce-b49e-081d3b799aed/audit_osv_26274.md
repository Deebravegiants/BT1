# [H] drm/amd/pm: fix a double-free in si_dpm_init

## Summary
Severity: High
Advisory: CVE-2023-52691
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52691
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.19.306, >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/pm: fix a double-free in si_dpm_init

When the allocation of
adev->pm.dpm.dyn_state.vddc_dependency_on_dispclk.entries fails,
amdgpu_free_extended_power_table is called to free some fields of adev.
However, when the control flow returns to si_dpm_sw_init, it goes to
label dpm_failed and calls si_dpm_fini, which calls
amdgpu_free_extended_power_table again and free those fields again. Thus
a double-free is triggered.

## References
- https://git.kernel.org/stable/c/06d95c99d5a4f5accdb79464076efe62e668c706
- https://git.kernel.org/stable/c/2bf47c89bbaca2bae16581ef1b28aaec0ade0334
- https://git.kernel.org/stable/c/ac16667237a82e2597e329eb9bc520d1cf9dff30
- https://git.kernel.org/stable/c/aeed2b4e4a70c7568d4a5eecd6a109713c0dfbf4
- https://git.kernel.org/stable/c/afe9f5b871f86d58ecdc45b217b662227d7890d0
- https://git.kernel.org/stable/c/ca8e2e251c65e5a712f6025e27bd9b26d16e6f4a
- https://git.kernel.org/stable/c/f957a1be647f7fc65926cbf572992ec2747a93f2
- https://git.kernel.org/stable/c/fb1936cb587262cd539e84b34541abb06e42b2f9
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52691.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52691
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
