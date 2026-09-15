# [H] net: airoha: fix BQL imbalance in TX path

## Summary
Severity: High
Advisory: CVE-2026-52983
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52983
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: airoha: fix BQL imbalance in TX path

Fix a possible BQL imbalance in airoha_dev_xmit(), where inflight
packets are accounted only for the AIROHA_NUM_TX_RING netdev TX
queues. The queue index is computed as:

    qid = skb_get_queue_mapping(skb) % ARRAY_SIZE(qdma->q_tx)
    txq = netdev_get_tx_queue(dev, qid);

However, airoha_qdma_tx_napi_poll() accounts completions across all
netdev TX queues (num_tx_queues), leading to inconsistent BQL
accounting.

Also reset all netdev TX queues in the ndo_stop callback.

## References
- https://git.kernel.org/stable/c/2d9f5a118205da2683ffcec78b9347f1f01a820e
- https://git.kernel.org/stable/c/aaad53a55812acd2355c0e5478896381e78b0110
- https://git.kernel.org/stable/c/ded2694247a55a16d0ebbe2d6f9139305c21457a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52983.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52983
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
