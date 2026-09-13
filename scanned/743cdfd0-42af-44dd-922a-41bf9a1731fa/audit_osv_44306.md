# [H] crypto: krb5 - use kfree_sensitive() for derived key buffers

## Summary
Severity: High
Advisory: CVE-2026-80924
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-80924
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.49, >=6.19.0 <7.1.13, >=7.2.0 <7.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: krb5 - use kfree_sensitive() for derived key buffers

crypto_krb5_prepare_encryption() and crypto_krb5_prepare_checksum()
free the buffer holding the freshly derived keys with plain kfree(),
leaving the key material behind in the freed slab object.

## References
- https://git.kernel.org/stable/c/731a5b6fb4c1705f9405d9029dd64ea81e336207
- https://git.kernel.org/stable/c/91b96dc9cc250cd16751f53de525cf3442ca0962
- https://git.kernel.org/stable/c/a1bf79365794783b19f5b09e8a23f7ee311e8931
- https://git.kernel.org/stable/c/f7d53dd3f267e46a784f219a75072f2f400d42b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80924.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
