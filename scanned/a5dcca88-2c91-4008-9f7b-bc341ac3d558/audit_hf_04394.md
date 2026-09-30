# [H] `CDPVault.sol#liquidatePositionBadDebt`

## Summary
Severity: High
Contest weight: 0.5212
Dataset id: 21706
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the liquidation routine of the CDPVault contract, specifically the liquidatePositionBadDebt function. When a position with bad debt is liquidated, the implementation deliberately overwrites the calculated profit variable with zero before invoking the pool's repayCreditAccount method. This erroneous assignment prevents the pool from receiving the correct profit amount, and the subsequent logic that should mint profit shares to the treasury (and ultimately to lpETH stakers) is never executed. The root cause is a logical flaw in the handling of profit and loss parameters: the function passes only the debt and accrued interest to the pool, omitting the actual profit value and not correctly propagating any loss. An attacker or any user who can trigger a bad‑debt liquidation can therefore cause the protocol to skip profit distribution, effectively causing funds that should have been allocated to LP token holders to disappear. The impact is that lpETH stakers receive no additional shares after liquidation, their expected returns are reduced, and the overall accounting of the vault becomes inconsistent with its business logic, which assumes that profit from liquidations is shared with stakeholders. This condition occurs whenever liquidatePositionBadDebt is called, i.e., during bad‑debt liquidations, and it affects all participants who hold lpETH tokens as well as the protocol treasury that relies on profit minting. The issue was uncovered during a Code4rena audit that examined the vault’s liquidation pathways. It can be hard to notice because the contract does not revert or emit an explicit error; the profit simply remains zero, leading to silent loss of expected earnings. To remediate, the contract should forward the actual profit and loss values to pool.repayCreditAccount, for example by calling pool.repayCreditAccount(debtData.debt, debtData.accruedInterest, loss), and the pool should conditionally mint profit shares when profit > 0 while handling loss > 0 appropriately. This aligns the implementation with the intended accounting model where profit is distributed to LPs and loss is accounted for, preventing silent fund disappearance.

## Recommendation
In CDPVault, change to `pool.repayCreditAccount(debtData.debt, debtData.accruedInterest, loss)`.

In PoolV3:

```solidity
if (profit > 0) {
    _mint(treasury, convertToShares(profit)); // U:[LP-14B]
}
if (loss > 0)
// } else if (loss > 0) {
...
```
