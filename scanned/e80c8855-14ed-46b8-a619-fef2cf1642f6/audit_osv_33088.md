# [H] s390/mm: Do not map lowcore with identity mapping

## Summary
Severity: High
Advisory: CVE-2025-38733
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-38733
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/mm: Do not map lowcore with identity mapping

Since the identity mapping is pinned to address zero the lowcore is always
also mapped to address zero, this happens regardless of the relocate_lowcore
command line option. If the option is specified the lowcore is mapped
twice, instead of only once.

This means that NULL pointer accesses will succeed instead of causing an
exception (low address protection still applies, but covers only parts).
To fix this never map the first two pages of physical memory with the
identity mapping.

## References
- https://git.kernel.org/stable/c/1d7864acd497cb468a998d44631f84896f885e85
- https://git.kernel.org/stable/c/30bf5728bb217a6d1ba73f44094c9b9c6bc9a567
- https://git.kernel.org/stable/c/93f616ff870a1fb7e84d472cad0af651b18f9f87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38733.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38733
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
