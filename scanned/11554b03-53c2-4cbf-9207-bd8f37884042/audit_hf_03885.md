# [M] Liquidating pending quotes doesn't return trad-

## Summary
Severity: Medium
Contest weight: 0.1069
Dataset id: 20168
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user is liquidated, the trading fees of the pending quotes aren't returned.
When a pending/locked quote is canceled, the trading fee is sent back to party A, e.g.
ore/contracts/facets/PartyA/PartyAFacetImpl.sol#L136
ore/contracts/facets/PartyA/PartyAFacetImpl.sol#L227
But, when a pending quote is liquidated, the trading fee is not used for the liquidation. Instead, the fee collector keeps the funds:
These funds should be used to cover the liquidation. Since no trade has been executed, the fee collector shouldn't earn anything.
Liquidation doesn't use paid trading fees to cover outstanding balances. Instead, the funds are kept by the fee collector.

## Recommendation
Return the funds to party A. If party A is being liquidated, use the funds to cover the liquidation. Otherwise, party A keeps the funds.
