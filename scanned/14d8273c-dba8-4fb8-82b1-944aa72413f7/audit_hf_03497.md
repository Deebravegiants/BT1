# [M] Inadequate systemic risk-controls to support cross-asset collateralization across a wide range of assets

## Summary
Severity: Medium
Contest weight: 0.3476
Dataset id: 19121
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Current Dolomite Margin risk controls can be classified into two categories:
 - Account-level risk controls
 - Systemic risk controls

Dolomite incorporates a robust risk monitoring architecture that comprehensively verifies the final state's validity at the conclusion of each operation. An operation, which encompasses a collection of transactions, undergoes thorough system checks to ensure the integrity and accuracy of the final state. This calculation happens in [`OperationImpl::_verifyFinalState`](https://github.com/dolomite-exchange/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/OperationImpl.sol#L309) where both account-level and system-level risk is measured.

While the existing systemic risk controls address various aspects, such as borrowing limits, supply limits, collateral-only mode, and oracle sentinel, they fail to consider the systemic risk introduced by cross-asset collateralisation.

The creation of virtual liquidity without sufficient token backing can expose the protocol to risks associated with liquidity squeezes, freezes, and fluctuating asset correlations. This is similar to fractional banking in traditional finance, i.e., if a bank lends more than 10x its deposits, the bank exposes itself to insolvency risks due to tight liquidity conditions.

In the case of Dolomite Margin, the ratio of virtual liquidity to actual token balance can be considered as leverage - the higher the leverage, the greater the insolvency risk. If this virtual liquidity is utilised as collateral for additional borrowing, it can further amplify the leverage.

Higher protocol leverage can directly increase the risk of insolvency during periods of tight liquidity. Since such risks are attributed to extremely rare black-swan type of events, we evaluate the severity to MEDIUM.

## Proof of Concept
Consider a USDT de-peg scenario where we see the following events unfold:

1. Virtual USDT holders will scramble to convert to real USDT liquidity, attempting to offload it anywhere possible.
2. Speculators, seeing an opportunity, will initiate cross-collateral borrow positions in USDT. High potential profits in short periods can make them overlook even steep interest rates at higher utilisation levels.
3. These virtual USDT tokens can then be swiftly exchanged for other stable tokens within Dolomite's internal pools.
4. Liquidators might hesitate to liquidate positions with USDT as collateral, anticipating potential high slippage in one-sided markets.

All the above factors may trigger a cascading effect, leading Dolomite to accumulate substantial USDT bad debt. While borrow/supply limits exist, introducing additional safeguards to curb unbacked liquidity could better equip Dolomite to manage potential contagion scenario.

## Recommendation
To enhance the system's robustness, consider adding a systemic risk measure to the `OperationImpl::_verifyFinalState` function that caps the leverage per market. Consider implementing a cap on leverage for less liquid markets restricting the ability of users to open cross asset borrowing positions without having enough real liquidity.
