# [M] Blast yield is claimed stepwise,

## Summary
Severity: Medium
Contest weight: 0.0982
Dataset id: 1869
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Blast yield is claimed stepwise, which allows arbitrage of the vault
Vaults deployed on Blast will use BlastVault to claim the yield. However this mechanism introduces step-wise operations, which are instant increases in share value upon claim.
This can be arbitraged by MEV bots and users, by simply watching the mempool and sandwiching the claim TX.
Example:
1. Alice sees that the admin is gonna claim 1 WETH in 80 WETH pool
2. Alice sandwiches that TX by depositing 20 WETH and then withdrawing it right after the claim
3. Alice hold 20% of the pool shares during the claim operation, so she receives 20% of the value (0.2 ETH)
Users can MEV claim.

## Recommendation
Consider adding deposit/withdraw windows.
