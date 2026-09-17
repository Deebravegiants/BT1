# [H] LoongArch: KVM: Avoid overflow with array index

## Summary
Severity: High
Advisory: CVE-2025-38367
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38367
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Avoid overflow with array index

The variable index is modified and reused as array index when modify
register EIOINTC_ENABLE. There will be array index overflow problem.

## References
- https://git.kernel.org/stable/c/080e8d2ecdfde588897aa8a87a8884061f4dbbbb
- https://git.kernel.org/stable/c/2cc84c4b0d70d42e291862ecc848890d18e1004a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38367.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
