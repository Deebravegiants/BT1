# [H] drm/msm/gem: prevent integer overflow in msm_ioctl_gem_submit()

## Summary
Severity: High
Advisory: CVE-2024-52559
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-52559
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.6.80, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/gem: prevent integer overflow in msm_ioctl_gem_submit()

The "submit->cmd[i].size" and "submit->cmd[i].offset" variables are u32
values that come from the user via the submit_lookup_cmds() function.
This addition could lead to an integer wrapping bug so use size_add()
to prevent that.

Patchwork: https://patchwork.freedesktop.org/patch/624696/

## References
- https://git.kernel.org/stable/c/2b99b2c4621d13bd4374ef384e8f1fc188d0a5df
- https://git.kernel.org/stable/c/2f1845e46c41ed500789d53dc45b383b7745c96c
- https://git.kernel.org/stable/c/3a47f4b439beb98e955d501c609dfd12b7836d61
- https://git.kernel.org/stable/c/e43a0f1327a1ee70754f8a0de6e0262cfa3e0b87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52559.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52559
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
