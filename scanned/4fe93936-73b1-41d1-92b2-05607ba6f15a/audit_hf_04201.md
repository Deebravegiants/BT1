# [C] C-08 | Collateral Modification Abused To Levy LP Fees

## Summary
Severity: Critical
Contest weight: 0.3062
Dataset id: 21094
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When depositing and withdrawing sUSD collateral, a fee is accrued in the depositMarketUsd and
withdrawMarketUsd functions in the MarketManagerModule. For example, in a deposit, the fee is
subtracted from the amount and added to creditCapacityD18:
market.creditCapacityD18 += (amount - feeAmount)
However, these fees are handled only inside the Synthetix V3 system, whereas the BFP market adds
the entire deposited amount to the trader balance, neglecting the fees:
accountMargin.collaterals[synthMarketId] += absAmountDelta
This way the trader does not experience the fees levied from their collateral deposit and withdrawal
actions, rather the liquidity providers and potentially traders with unrealized profits are affected. This
can be exploited to manipulate creditCapacityD18 and netIssuanceD18 by continuously calling
modifyCollateral in order to increase netIssuanceD18 and decrease creditCapacityD18.
Anyone can batch deposit-withdraw calls in one TX using Morpho flashloans (0% fees) in order to
maximize the impact with minimal capital requirements.
Increasing netIssuanceD18 will report more debt for the LPs than actually exists and lower their
profits. Decreasing creditCapacityD18 could lead to traders getting stuck inside the BFP as
withdrawMarketUsd reverts inside getWithdrawableMarketUsd and withdrawMarketCollateral can
revert with newWithdrawableMarketUsd < 0.

## Recommendation
Account for the fees being charged in the BFP market, reducing the amount of collateral traders are
credited with upon deposits by the fee amount and reducing the amount of collateral traders
ultimately redeem from the Synthetix V3 system by the fees.
