# [H] drm/msm/dp: Free resources after unregistering them

## Summary
Severity: High
Advisory: CVE-2023-53316
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53316
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dp: Free resources after unregistering them

The DP component's unbind operation walks through the submodules to
unregister and clean things up. But if the unbind happens because the DP
controller itself is being removed, all the memory for those submodules
has just been freed.

Change the order of these operations to avoid the many use-after-free
that otherwise happens in this code path.

Patchwork: https://patchwork.freedesktop.org/patch/542166/

## References
- https://git.kernel.org/stable/c/3c3f3d35f5e05c468b048eb42a4f8c62c6655692
- https://git.kernel.org/stable/c/4e9f1a2367aea7d61f6781213e25313cd983b0d7
- https://git.kernel.org/stable/c/5c3278db06e332fdc14f3f297499fb88ded264d2
- https://git.kernel.org/stable/c/c67a55f7cc8d767d624235bf1bcd0947e56abe0f
- https://git.kernel.org/stable/c/ca47d0dc00968358c136a1847cfed550cedfd1b5
- https://git.kernel.org/stable/c/fa0048a4b1fa7a50c8b0e514f5b428abdf69a6f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53316.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53316
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
