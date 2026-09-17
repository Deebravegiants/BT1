# [H] wifi: mac80211: always free skb on ieee80211_tx_prepare_skb() failure

## Summary
Severity: High
Advisory: CVE-2026-23444
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23444
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.84, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: always free skb on ieee80211_tx_prepare_skb() failure

ieee80211_tx_prepare_skb() has three error paths, but only two of them
free the skb. The first error path (ieee80211_tx_prepare() returning
TX_DROP) does not free it, while invoke_tx_handlers() failure and the
fragmentation check both do.

Add kfree_skb() to the first error path so all three are consistent,
and remove the now-redundant frees in callers (ath9k, mt76,
mac80211_hwsim) to avoid double-free.

Document the skb ownership guarantee in the function's kdoc.

## References
- https://git.kernel.org/stable/c/06e769dddcbeb3baf2ce346273b53dd61fdbecf4
- https://git.kernel.org/stable/c/3b4d27acafaeab478fd24f79ad6e593a892828b9
- https://git.kernel.org/stable/c/50f1b690b4868923fbd242298def2fb88662f108
- https://git.kernel.org/stable/c/5ef8ca1c164786da24169af155c1ca1ff1353cf8
- https://git.kernel.org/stable/c/905ef207d5ed99ca64adfe39fba9ac46e434327a
- https://git.kernel.org/stable/c/9a779d1f480e83720b5384adf165604e7ee226bd
- https://git.kernel.org/stable/c/d5ad6ab61cbd89afdb60881f6274f74328af3ee9
- https://git.kernel.org/stable/c/f77b51bcee7be2bb686b5f7a2d4a1921e4bdb9f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23444.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23444
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
