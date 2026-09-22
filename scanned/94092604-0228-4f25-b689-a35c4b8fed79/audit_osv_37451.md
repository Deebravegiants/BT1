# [H] rxrpc: Fix buffer overread in rxgk_do_verify_authenticator()

## Summary
Severity: High
Advisory: CVE-2026-31631
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31631
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix buffer overread in rxgk_do_verify_authenticator()

Fix rxgk_do_verify_authenticator() to check the buffer size before checking
the nonce.

## References
- https://git.kernel.org/stable/c/1c4422d8be81718ecb15d79aedff607323085201
- https://git.kernel.org/stable/c/794586789800b16dcbe235452494f4223ac80413
- https://git.kernel.org/stable/c/f564af387c8c28238f8ebc13314c589d7ba8475d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31631.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31631
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
