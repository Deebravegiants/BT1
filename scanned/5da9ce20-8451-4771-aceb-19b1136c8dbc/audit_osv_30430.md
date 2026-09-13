# [M] drm: zynqmp_dp: Fix integer overflow in zynqmp_dp_rate_get()

## Summary
Severity: Medium
Advisory: CVE-2024-52557
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-52557
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: zynqmp_dp: Fix integer overflow in zynqmp_dp_rate_get()

This patch fixes a potential integer overflow in the zynqmp_dp_rate_get()

The issue comes up when the expression
drm_dp_bw_code_to_link_rate(dp->test.bw_code) * 10000 is evaluated using 32-bit
Now the constant is a compatible 64-bit type.

Resolves coverity issues: CID 1636340 and CID 1635811

## References
- https://git.kernel.org/stable/c/325d889c5403ba20a24097f64c32d27ab993c2c3
- https://git.kernel.org/stable/c/67a615c5cb6dc33ed35492dc0d67e496cbe8de68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52557.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52557
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
