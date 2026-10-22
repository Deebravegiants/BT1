# [M] LDTR-3 | Liquidations Prevented By Slippage

## Summary
Severity: Medium
Contest weight: 0.0777
Dataset id: 19572
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because some liquidations require a swap, they could be prevented if a malicious actor front-runs the transaction and moves the pool price out of the acceptable range. The malicious actor could sandwich the transaction to undo this price manipulation so that minimal capital is lost. Consequently, the liquidations will be prevented by an insufficient output amount revert, leaving bad debt in the protocol.

## Recommendation
Use an aggregator and/or ensure the discount is large enough to meet slippage requirements. Furthermore, consider allowing unprofitable liquidations to occur, marking the forceful liquidation with a boolean flag if necessary.
