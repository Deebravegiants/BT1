# [M] drm/msm/dsi: Add missing check for alloc_ordered_workqueue

## Summary
Severity: Medium
Advisory: CVE-2023-53223
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53223
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dsi: Add missing check for alloc_ordered_workqueue

Add check for the return value of alloc_ordered_workqueue as it may return
NULL pointer and cause NULL pointer dereference.

Patchwork: https://patchwork.freedesktop.org/patch/517646/

## References
- https://git.kernel.org/stable/c/115906ca7b535afb1fe7b5406c566ccd3873f82b
- https://git.kernel.org/stable/c/25a6499b1a53d854eda2b161b5c8a20296515dbe
- https://git.kernel.org/stable/c/3a9a4a9725c60f04326b5019a52ce15aee808506
- https://git.kernel.org/stable/c/3e18f157faeeb59034404569e8e07cbe1c0030a7
- https://git.kernel.org/stable/c/540c66180afd59309a442d3bf1f2393464c8b4c5
- https://git.kernel.org/stable/c/5dfe7a5386fde5a656ca06602b31bf50e26954cd
- https://git.kernel.org/stable/c/759ea5677c362fb1e3edc667260ba9f409dc931d
- https://git.kernel.org/stable/c/9257974858ee847b2e1fd552691b8ba5c2fc1c7b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53223.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53223
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
