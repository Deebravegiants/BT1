# [H] firmware: arm_ffa: Bound PARTITION_INFO_GET_REGS copies

## Summary
Severity: High
Advisory: CVE-2026-64520
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64520
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_ffa: Bound PARTITION_INFO_GET_REGS copies

The register-based PARTITION_INFO_GET path trusted the firmware-provided
indices when copying partition descriptors into the caller buffer.
Reject inconsistent counts or index progressions so the copy loop cannot
write past the allocated array.

(fixed cur_idx when exactly one descriptor in the first fragment)

## References
- https://git.kernel.org/stable/c/3974ea1938406f9bfa7c1f48d4e43533f447bb08
- https://git.kernel.org/stable/c/79d95c02ae0a95e6e80e8e92b7ca74ecee02854f
- https://git.kernel.org/stable/c/f39bc7ebe75e2186b417a024a7f7e2fd4cc7eb95
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64520.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64520
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
