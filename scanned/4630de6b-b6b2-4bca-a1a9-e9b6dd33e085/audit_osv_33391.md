# [H] KVM: arm64: Check the untrusted offset in FF-A memory share

## Summary
Severity: High
Advisory: CVE-2025-40266
Aliases: A-439862698, ASB-A-439862698
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40266
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <6.6.118, >=6.7.0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Check the untrusted offset in FF-A memory share

Verify the offset to prevent OOB access in the hypervisor
FF-A buffer in case an untrusted large enough value
[U32_MAX - sizeof(struct ffa_composite_mem_region) + 1, U32_MAX]
is set from the host kernel.

## References
- https://git.kernel.org/stable/c/103e17aac09cdd358133f9e00998b75d6c1f1518
- https://git.kernel.org/stable/c/bc1909ef38788f2ee3d8011d70bf029948433051
- https://git.kernel.org/stable/c/f9f1aed6c8a3427900da3121e1868124854569c3
- https://git.kernel.org/stable/c/fc3139d9f4c1fe1c7d5f25f99676bd8e9c6a1041
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40266.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40266
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
