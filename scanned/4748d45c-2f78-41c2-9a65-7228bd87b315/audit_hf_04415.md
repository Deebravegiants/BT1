# [M] M-10 | Virtual Inventory Ignored On Withdrawal

## Summary
Severity: Medium
Contest weight: 0.2116
Dataset id: 21891
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When withdrawing from a GM market in GMX V2, no price impact is applied since the withdrawn tokens are taken at the ratio of pool balances of the backing liquidity for the market. However if the market is within a virtual inventory, this ratio which was withdrawn directly from the market may have a negative impact on the virtual inventory (VI), but is ignored since no price impact is applied on withdrawal. Consider the following scenario: • Markets A, B, and C are all backed by WETH/USDC and make up a VI • Market A holds $100 of WETH and $200 of USDC • Market B holds $200 of WETH and $100 of USDC • Market C holds $100 of WETH and $100 of USDC • The total VI balances are $400 WETH & $400 USDC, the VI is balanced • User A withdraws 50% of the GM supply from Market A • Market A now holds $50 of WETH and $100 of USDC, ignoring fees • The total VI balances are $350 WETH and $300 USDC, the VI is now unbalanced Since there is no way to be positively impacted for balancing the virtual inventory, no value can be directly extracted this way. Though this leads to cases where the virtual inventory is negatively imbalanced, affecting other users who experience subsequent negative impact within the same virtual inventory on swaps and deposits, but while failing to negatively impact the user who created the imbalance. Additionally, as the virtual inventory was implemented to disincentivize profitable manipulations in price impact across similar markets, ignoring the VI on withdrawals may allow a case where this is not sufficiently protected against, though none have been identified at this time.

## Recommendation
Consider consulting the virtual inventory and applying the relevant negative impact if a withdrawal would cause an unwanted imbalance.
