# [M] The most important invariant will be broken.

## Summary
Severity: Medium
Contest weight: 0.0846
Dataset id: 22962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Order tokens can violate key invariants through transfer or transferFrom. OFT version ORDER token on OFTs contracts (all L2s) == the ORDER balance of OrderAdapter on native OrderToken contract (Ethereum). When users hold order tokens on Ethereum, they can send order tokens to OrderAdapter via transfer or transferFrom. This increases the number of order tokens in the OrderAdapter, thus violating the aforementioned 'most important invariant'. The most important invariant will be broken.

## Recommendation
It is recommended to prohibit transfer and transferFrom to the OrderAdapter address or to restrict transfers to this address to whitelist users only.
