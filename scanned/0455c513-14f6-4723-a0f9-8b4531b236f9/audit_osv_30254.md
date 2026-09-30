# [H] NFSD: Initialize struct nfsd4_copy earlier

## Summary
Severity: High
Advisory: CVE-2024-50241
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50241
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.3 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Initialize struct nfsd4_copy earlier

Ensure the refcount and async_copies fields are initialized early.
cleanup_async_copy() will reference these fields if an error occurs
in nfsd4_copy(). If they are not correctly initialized, at the very
least, a refcount underflow occurs.

## References
- https://git.kernel.org/stable/c/059434d23c4578d9d02efb92d848ea21bc640112
- https://git.kernel.org/stable/c/421f1a2a1afb47d88de09457ef7687e1df7bc997
- https://git.kernel.org/stable/c/63fab04cbd0f96191b6e5beedc3b643b01c15889
- https://git.kernel.org/stable/c/7267625baf365a969f1b25ded6f07b64bc90ec5b
- https://git.kernel.org/stable/c/c3074003fa6837c2b89a34d8d12d9463b59d22d6
- https://git.kernel.org/stable/c/e30a9a2f69c34a00a3cb4fd45c5d231929e66fb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50241.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
