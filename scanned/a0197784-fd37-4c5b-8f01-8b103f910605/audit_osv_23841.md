# [H] crypto: qat - add param check for RSA

## Summary
Severity: High
Advisory: CVE-2022-49563
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49563
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - add param check for RSA

Reject requests with a source buffer that is bigger than the size of the
key. This is to prevent a possible integer underflow that might happen
when copying the source scatterlist into a linear buffer.

## References
- https://git.kernel.org/stable/c/4d6d2adce08788b7667a6e58002682ea1bbf6a79
- https://git.kernel.org/stable/c/9714061423b8b24b8afb31b8eb4df977c63f19c4
- https://git.kernel.org/stable/c/f993321e50ba7a8ba4f5b19939e1772a921a1c42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49563.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49563
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
