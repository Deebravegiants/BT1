# [C] ksmbd: fix Preauh_HashValue race condition

## Summary
Severity: Critical
Advisory: CVE-2025-38561
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38561
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix Preauh_HashValue race condition

If client send multiple session setup requests to ksmbd,
Preauh_HashValue race condition could happen.
There is no need to free sess->Preauh_HashValue at session setup phase.
It can be freed together with session at connection termination phase.

## References
- https://git.kernel.org/stable/c/44a3059c4c8cc635a1fb2afd692d0730ca1ba4b6
- https://git.kernel.org/stable/c/6613887da1d18dd2ecfd6c6148a873c4d903ebdc
- https://git.kernel.org/stable/c/7d7c0c5304c88bcbd7a85e9bcd61d27e998ba5fc
- https://git.kernel.org/stable/c/b69fd87076daa66f3d186bd421a7b0ee0cb45829
- https://git.kernel.org/stable/c/edeecc7871e8fc0878d53ce286c75040a0e38f6c
- https://git.kernel.org/stable/c/fbf5c0845ed15122a770bca9be1d9b60b470d3aa
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38561.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38561
- https://www.zerodayinitiative.com/advisories/ZDI-25-916/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
