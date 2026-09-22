# [M] drm: msm: fix possible memory leak in mdp5_crtc_cursor_set()

## Summary
Severity: Medium
Advisory: CVE-2022-49467
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49467
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: msm: fix possible memory leak in mdp5_crtc_cursor_set()

drm_gem_object_lookup will call drm_gem_object_get inside. So cursor_bo
needs to be put when msm_gem_get_and_pin_iova fails.

## References
- https://git.kernel.org/stable/c/33546183c16c7b9650682dc610bedd732d9c6919
- https://git.kernel.org/stable/c/449374565f349d4233beec811d4286fdfe5de44b
- https://git.kernel.org/stable/c/656aa3c51fc662064f17179b38ec3ce43af53bca
- https://git.kernel.org/stable/c/947a844bb3ebff0f4736d244d792ce129f6700d7
- https://git.kernel.org/stable/c/d544880482a5558ec06393b1b3d5dc9275b7a32b
- https://git.kernel.org/stable/c/d63ffe3fb3f8327ca21cf91b6a14a2961bc629b4
- https://git.kernel.org/stable/c/f8cd192752a1f613b14eee77783c6f0aebb49691
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49467.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49467
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
