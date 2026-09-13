# [M] CVE-2021-47610

## Summary
Severity: Medium
Advisory: CVE-2021-47610
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47610
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix null ptr access msm_ioctl_gem_submit()

Fix the below null pointer dereference in msm_ioctl_gem_submit():

 26545.260705:   Call trace:
 26545.263223:    kref_put+0x1c/0x60
 26545.266452:    msm_ioctl_gem_submit+0x254/0x744
 26545.270937:    drm_ioctl_kernel+0xa8/0x124
 26545.274976:    drm_ioctl+0x21c/0x33c
 26545.278478:    drm_compat_ioctl+0xdc/0xf0
 26545.282428:    __arm64_compat_sys_ioctl+0xc8/0x100
 26545.287169:    el0_svc_common+0xf8/0x250
 26545.291025:    do_el0_svc_compat+0x28/0x54
 26545.295066:    el0_svc_compat+0x10/0x1c
 26545.298838:    el0_sync_compat_handler+0xa8/0xcc
 26545.303403:    el0_sync_compat+0x188/0x1c0
 26545.307445:   Code: d503201f d503201f 52800028 4b0803e8 (b8680008)
 26545.318799:   Kernel panic - not syncing: Oops: Fatal exception

## References
- https://git.kernel.org/stable/c/26d776fd0f79f093a5d0ce1a4c7c7a992bc3264c
- https://git.kernel.org/stable/c/f6db3d98f876870c35e96693cfd54752f6199e59
