# [H] ksmbd: Compare MACs in constant time

## Summary
Severity: High
Advisory: CVE-2026-23364
Ecosystem: Linux
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23364
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.210, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Compare MACs in constant time

To prevent timing attacks, MAC comparisons need to be constant-time.
Replace the memcmp() with the correct function, crypto_memneq().

## References
- https://git.kernel.org/stable/c/2cdc56ed67615ba0921383a688f24415ebe065f3
- https://git.kernel.org/stable/c/307afccb751f542246bd5dc68a2c1ffe1a78418c
- https://git.kernel.org/stable/c/8a665d733940592e671ec6afadcd0be80a091a80
- https://git.kernel.org/stable/c/93c0a22fec914ec4b697e464895a0f594e29fb28
- https://git.kernel.org/stable/c/c5794709bc9105935dbedef8b9cf9c06f2b559fa
- https://git.kernel.org/stable/c/cd52a0e309659537048a864211abc3ea4c5caa63
- https://git.kernel.org/stable/c/f4588b85efd6007d46b80aa1b9fb746628ffb3dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23364.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
