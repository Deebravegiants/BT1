# [H] drm/amdgpu/vce1: Fix VCE 1 firmware size and offsets

## Summary
Severity: High
Advisory: CVE-2026-64516
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64516
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vce1: Fix VCE 1 firmware size and offsets

The VCPU BO contains the actual FW at an offset, but
it was not calculated into the VCPU BO size.
Subtract this from the FW size to make sure there is
no out of bounds access.

Make sure the stack and data offsets are aligned to
the 32K TLB size.

Check that the FW microcode actually fits in the
space that is reserved for it.

(cherry picked from commit c16fe59f622a080fc457a57b3e8f14c780699449)

## References
- https://git.kernel.org/stable/c/3e5a1d5bb2ff061e64c7992f8e5404dfd4c2d0f3
- https://git.kernel.org/stable/c/ce0de178ef08408f6ba8f2e9a13bf52fbe5852f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64516.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64516
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
