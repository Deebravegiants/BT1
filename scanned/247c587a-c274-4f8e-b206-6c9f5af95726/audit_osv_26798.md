# [H] netfilter: nf_tables: fix underflow in chain reference counter

## Summary
Severity: High
Advisory: CVE-2023-54035
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54035
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: fix underflow in chain reference counter

Set element addition error path decrements reference counter on chains
twice: once on element release and again via nft_data_release().

Then, d6b478666ffa ("netfilter: nf_tables: fix underflow in object
reference counter") incorrectly fixed this by removing the stateful
object reference count decrement.

Restore the stateful object decrement as in b91d90368837 ("netfilter:
nf_tables: fix leaking object reference count") and let
nft_data_release() decrement the chain reference counter, so this is
done only once.

## References
- https://git.kernel.org/stable/c/9c959671abc7d4ffdf34eed10c64492d43cb6a3c
- https://git.kernel.org/stable/c/b068314fd8ce751a7f906e55bb90f3551815f1a0
- https://git.kernel.org/stable/c/b389139f12f287b8ed2e2628b72df89a081f0b59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54035.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54035
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
