# [H] crypto: x86/aegis - Add missing error checks

## Summary
Severity: High
Advisory: CVE-2025-39789
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39789
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: x86/aegis - Add missing error checks

The skcipher_walk functions can allocate memory and can fail, so
checking for errors is necessary.

## References
- https://git.kernel.org/stable/c/3d9eb180fbe8828cce43bce4c370124685b205c3
- https://git.kernel.org/stable/c/475104178f4d30e749ee4f5473c87f692b93bebb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39789.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39789
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
