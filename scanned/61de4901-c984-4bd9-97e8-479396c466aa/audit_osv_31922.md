# [M] drm/amdgpu: NULL-check BO's backing store when determining GFX12 PTE flags

## Summary
Severity: Medium
Advisory: CVE-2025-21990
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-21990
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: NULL-check BO's backing store when determining GFX12 PTE flags

PRT BOs may not have any backing store, so bo->tbo.resource will be
NULL. Check for that before dereferencing.

(cherry picked from commit 3e3fcd29b505cebed659311337ea03b7698767fc)

## References
- https://git.kernel.org/stable/c/6cc30748e17ea2a64051ceaf83a8372484e597f1
- https://git.kernel.org/stable/c/72235808eabea93055b459a63443bd9cd6b08aa4
- https://git.kernel.org/stable/c/af23e39b9e9280b1f6299b6f2fa090a1694240ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21990.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
