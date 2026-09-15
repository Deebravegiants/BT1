# [H] drm/msm/dsi: fix memory corruption with too many bridges

## Summary
Severity: High
Advisory: CVE-2022-50368
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50368
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.264, >=4.20.0 <5.4.223, >=5.5.0 <5.10.153, >=5.11.0 <5.15.77, >=5.16.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dsi: fix memory corruption with too many bridges

Add the missing sanity check on the bridge counter to avoid corrupting
data beyond the fixed-sized bridge array in case there are ever more
than eight bridges.

Patchwork: https://patchwork.freedesktop.org/patch/502668/

## References
- https://git.kernel.org/stable/c/21c4679af01f1027cb559330c2e7d410089b2b36
- https://git.kernel.org/stable/c/2e786eb2f9cebb07e317226b60054df510b60c65
- https://git.kernel.org/stable/c/4e5587cddb334f7a5bb1c49ea8bbfc966fafe1b8
- https://git.kernel.org/stable/c/9f035d1fb30648fe70ee01627eb131c56d699b35
- https://git.kernel.org/stable/c/e83b354890a3c1d5256162f87a6cc38c47ae7f20
- https://git.kernel.org/stable/c/f649ed0e1b7a1545f8e27267d3c468b3cb222ece
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50368.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
