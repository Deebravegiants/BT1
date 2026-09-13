# [H] ksmbd: fix racy issue under cocurrent smb2 tree disconnect

## Summary
Severity: High
Advisory: CVE-2023-53358
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53358
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.145, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix racy issue under cocurrent smb2 tree disconnect

There is UAF issue under cocurrent smb2 tree disconnect.
This patch introduce TREE_CONN_EXPIRE flags for tcon to avoid cocurrent
access.

## References
- https://git.kernel.org/stable/c/30210947a343b6b3ca13adc9bfc88e1543e16dd5
- https://git.kernel.org/stable/c/39366b47a59d46af15ac57beb0996268bf911f6a
- https://git.kernel.org/stable/c/b36295c17fb97424406f0c3ab321b1ccaabb9be8
- https://git.kernel.org/stable/c/bd80d35725a0cf4df9307bfe2f1a3b2cb983d8e6
- https://git.kernel.org/stable/c/dc1c17716c099c90948ebb83e2170dd75a3be6b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53358.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53358
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
