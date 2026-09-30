# [H] crypto: marvell/cesa - Handle zero-length skcipher requests

## Summary
Severity: High
Advisory: CVE-2025-38173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38173
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: marvell/cesa - Handle zero-length skcipher requests

Do not access random memory for zero-length skcipher requests.
Just return 0.

## References
- https://git.kernel.org/stable/c/32d3e8049a8b60f18c5c39f5931bfb1130ac11c9
- https://git.kernel.org/stable/c/5e9666ac8b94c978690f937d59170c5237bd2c45
- https://git.kernel.org/stable/c/7894694b5d5b2ecfd7fb081d6f60b9e169ab4d13
- https://git.kernel.org/stable/c/78ea1ff6cb413a03ff6f7af4e28e24b4461a0965
- https://git.kernel.org/stable/c/8a4e047c6cc07676f637608a9dd675349b5de0a7
- https://git.kernel.org/stable/c/c064ae2881d839709bd72d484d5f2af157f46024
- https://git.kernel.org/stable/c/c9610dda42bd382a96f97e68825cb5f66cd9e1dc
- https://git.kernel.org/stable/c/e1cc69da619588b1488689fe3535a0ba75a2b0e7
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38173.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
