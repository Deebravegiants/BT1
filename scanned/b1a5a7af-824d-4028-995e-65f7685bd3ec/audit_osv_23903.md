# [M] drm/i915: fix a possible refcount leak in intel_dp_add_mst_connector()

## Summary
Severity: Medium
Advisory: CVE-2022-49644
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49644
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: fix a possible refcount leak in intel_dp_add_mst_connector()

If drm_connector_init fails, intel_connector_free will be called to take
care of proper free. So it is necessary to drop the refcount of port
before intel_connector_free.

(cherry picked from commit cea9ed611e85d36a05db52b6457bf584b7d969e2)

## References
- https://git.kernel.org/stable/c/505114dda5bbfd07f4ce9a2df5b7d8ef5f2a1218
- https://git.kernel.org/stable/c/592f3bad00b7e2a95a6fb7a4f9e742c061c9c3c1
- https://git.kernel.org/stable/c/72f231b9a88abcfac9f5ddaa1a0aacb3f9f87ba5
- https://git.kernel.org/stable/c/85144df9ff4652816448369de76897c57cbb1b93
- https://git.kernel.org/stable/c/a91522b4279bebb098106a19b91f82b9c3213be9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49644.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49644
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
