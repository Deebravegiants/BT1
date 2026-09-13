# [M] net: remove two BUG() from skb_checksum_help()

## Summary
Severity: Medium
Advisory: CVE-2022-49497
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49497
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: remove two BUG() from skb_checksum_help()

I have a syzbot report that managed to get a crash in skb_checksum_help()

If syzbot can trigger these BUG(), it makes sense to replace
them with more friendly WARN_ON_ONCE() since skb_checksum_help()
can instead return an error code.

Note that syzbot will still crash there, until real bug is fixed.

## References
- https://git.kernel.org/stable/c/312c43e98ed190bd8fd7a71a0addf9539d5b8ab1
- https://git.kernel.org/stable/c/6320ae1b5876c30bf98203b6a5abe8b5c45e6a04
- https://git.kernel.org/stable/c/b1320c9a4d30ff54b824a8ad6036e0b5fb4c5e73
- https://git.kernel.org/stable/c/d5281245f3502e960cb6b89348767b935379cee3
- https://git.kernel.org/stable/c/d7ea0d9df2a6265b2b180d17ebc64b38105968fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49497.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49497
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
