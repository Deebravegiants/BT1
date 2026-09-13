# [H] drm/msm/dpu: Add mutex lock in control vblank irq

## Summary
Severity: High
Advisory: CVE-2023-52586
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52586
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dpu: Add mutex lock in control vblank irq

Add a mutex lock to control vblank irq to synchronize vblank
enable/disable operations happening from different threads to prevent
race conditions while registering/unregistering the vblank irq callback.

v4: -Removed vblank_ctl_lock from dpu_encoder_virt, so it is only a
    parameter of dpu_encoder_phys.
    -Switch from atomic refcnt to a simple int counter as mutex has
    now been added
v3: Mistakenly did not change wording in last version. It is done now.
v2: Slightly changed wording of commit message

Patchwork: https://patchwork.freedesktop.org/patch/571854/

## References
- https://git.kernel.org/stable/c/14f109bf74dd67e1d0469fed859c8e506b0df53f
- https://git.kernel.org/stable/c/45284ff733e4caf6c118aae5131eb7e7cf3eea5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52586.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
