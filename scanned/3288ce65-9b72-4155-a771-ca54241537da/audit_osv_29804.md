# [H] riscv: misaligned: Restrict user access to kernel memory

## Summary
Severity: High
Advisory: CVE-2024-46792
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46792
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: misaligned: Restrict user access to kernel memory

raw_copy_{to,from}_user() do not call access_ok(), so this code allowed
userspace to access any virtual memory address.

## References
- https://git.kernel.org/stable/c/a3b6ff6c896aee5ef9b581e40d0045ff04fcbc8c
- https://git.kernel.org/stable/c/b686ecdeacf6658e1348c1a32a08e2e72f7c0f00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46792.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46792
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
