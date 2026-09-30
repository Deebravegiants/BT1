# [H] wifi: ath9k: fix OOB access from firmware tx status queue ID

## Summary
Severity: High
Advisory: CVE-2026-74408
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74408
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath9k: fix OOB access from firmware tx status queue ID

ath_tx_edma_tasklet() accesses sc->tx.txq[ts.qid] where ts.qid is a
4-bit hardware field (0-15), but the txq array only has
ATH9K_NUM_TX_QUEUES (10) entries. A qid >= 10 causes an OOB array
access.

Add a bounds check on ts.qid before using it as an array index.

## References
- https://git.kernel.org/stable/c/336d4c8cd9b1646060ee690c881d465dfc09c6c0
- https://git.kernel.org/stable/c/46ca1451f61b598f45cb5259e066d305444d95fc
- https://git.kernel.org/stable/c/5435fd3edcb11c7cc4002847c83e9a50b49284dc
- https://git.kernel.org/stable/c/734db72d55ca578a344dfa33e30145032c074b25
- https://git.kernel.org/stable/c/7ce2f118a2389e8f0a64068c6fe7cc7d40639be0
- https://git.kernel.org/stable/c/a9e055ac62cb3fcea262d4b687ec73eed82b3379
- https://git.kernel.org/stable/c/f5931d06b45ed402572bfe5832fff15864ef5481
- https://git.kernel.org/stable/c/fb11083db9d7d6fb8f98bbba1cbfcf3fb7b4bf54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74408.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
