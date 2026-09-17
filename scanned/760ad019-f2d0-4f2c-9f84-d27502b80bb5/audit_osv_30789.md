# [H] drm: zynqmp_kms: Unplug DRM device before removal

## Summary
Severity: High
Advisory: CVE-2024-56538
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56538
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: zynqmp_kms: Unplug DRM device before removal

Prevent userspace accesses to the DRM device from causing
use-after-frees by unplugging the device before we remove it. This
causes any further userspace accesses to result in an error without
further calls into this driver's internals.

## References
- https://git.kernel.org/stable/c/2e07c88914fc5289c21820b1aa94f058feb38197
- https://git.kernel.org/stable/c/4fb97432e28a7e136b2d76135d50e988ada8e1af
- https://git.kernel.org/stable/c/692f52aedccbf79b212a1e14e3735192b4c24a7d
- https://git.kernel.org/stable/c/a17b9afe58c474657449cf87e238b1788200576b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56538.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56538
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
