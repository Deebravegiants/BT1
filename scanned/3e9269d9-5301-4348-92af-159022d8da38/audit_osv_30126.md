# [H] dm vdo: don't refer to dedupe_context after releasing it

## Summary
Severity: High
Advisory: CVE-2024-50091
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50091
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm vdo: don't refer to dedupe_context after releasing it

Clear the dedupe_context pointer in a data_vio whenever ownership of
the context is lost, so that vdo can't examine it accidentally.

## References
- https://git.kernel.org/stable/c/0808ebf2f80b962e75741a41ced372a7116f1e26
- https://git.kernel.org/stable/c/63ef073084c67878d7a92e15ad055172da3f05a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50091.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50091
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
