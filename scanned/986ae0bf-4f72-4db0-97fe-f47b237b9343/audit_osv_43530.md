# [H] wifi: mt76: mt7996: Fix possible token leak in mt7996_tx_prepare_skb()

## Summary
Severity: High
Advisory: CVE-2026-74323
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74323
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7996: Fix possible token leak in mt7996_tx_prepare_skb()

If link_conf or link_sta lookup fails in mt7996_tx_prepare_skb routine,
mt7996 driver leaks an already allocated tx token. Fix the issue
releasing the token in case of error.

## References
- https://git.kernel.org/stable/c/06e65d6cf80490bc0457d339595d1ed5a89e8899
- https://git.kernel.org/stable/c/831074096d0450308357271fc0ffd3f600a2487e
- https://git.kernel.org/stable/c/fa0e9aa92a7bc97fc42014c5efaaf1278fa92723
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74323.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74323
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
