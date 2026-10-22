# [M] The debt in `EligibilityDataProvider::requiredUsdValue`

## Summary
Severity: Medium
Contest weight: 0.6323
Dataset id: 21731
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a mis‑calculation in the eligibility logic that determines whether a user qualifies for LOOP token emissions. The contract is supposed to require that a user lock LP tokens whose USD value is at least 5 % of the user’s total debt, as described in the protocol documentation. However, the implementation first multiplies the raw debt amount by the required deposit ratio, then converts the result to a USD value using the LP price, and finally applies a price‑tolerance ratio. Because the requiredDepositRatio (5 %) and the priceToleranceRatio (90 %) are applied after the conversion, the effective threshold becomes 5 % × 90 % ≈ 4.5 % of the total debt, not the documented 5 %. In other words, the contract checks that the locked LP amount is greater than roughly 4.5 % of the debt, which is lower than intended. The root cause is an ordering error in the financial formula: the deposit ratio is applied to the debt before the conversion to USD, and the tolerance ratio is applied on top of that, shrinking the required collateral. An attacker can exploit this by providing slightly less LP than required, still passing the eligibility test, and then claim LOOP emissions that were meant only for properly collateralised users. The impact is that the protocol may distribute rewards to under‑collateralised positions, eroding the economic model and potentially draining reward funds. This condition occurs whenever the `isEligibleForRewards` function is called, because it relies on the faulty `requiredUsdValue` calculation. The affected parties include the protocol itself, token holders who fund the emissions, and honest users who expect the rules to be enforced. The issue was discovered during a Code4rena audit by comparing the on‑chain logic with the published documentation and with a reference implementation from Radiant Capital. It is hard to notice because the numbers involved are small percentages and the nested arithmetic hides the discrepancy; the contract still returns a non‑zero required value, so a superficial test may appear to work. To fix the problem, the required USD value should be computed by first converting the user’s total debt to USD, then applying the required deposit ratio, and finally comparing the result directly with the locked USD value, ensuring the threshold matches the documented 5 % of the total position. This aligns the code with the intended business rule and prevents reward leakage. The bug belongs to the class of financial‑formula errors where scaling factors are applied in the wrong order, leading to an eligibility check that is too permissive, causing users to receive rewards despite not meeting the advertised collateral requirement, which violates the protocol’s accounting assumptions and expected user experience where a user expects to need a 5 % lock but receives rewards with less.

## Proof of Concept
```solidity
function requiredUsdValue(address user) public view returns (uint256 required) {
    uint256 totalNormalDebt = vaultRegistry.getUserTotalDebt(user);
    required = (totalNormalDebt * requiredDepositRatio) / RATIO_DIVISOR;
    return _lockedUsdValue(required);
}
```
Here, the value of `totalNormalDebt` should be calculated first, and then the `requiredDepositRatio` should be applied to that value.

However, in the current implementation:
```solidity
function isEligibleForRewards(address _user) public view returns (bool) {
    uint256 lockedValue = lockedUsdValue(_user);

    uint256 requiredValue = (requiredUsdValue(_user) * priceToleranceRatio) / RATIO_DIVISOR;
    return requiredValue != 0 && lockedValue >= requiredValue;
}

function lockedUsdValue(address user) public view returns (uint256) {
    Balances memory _balances = IMultiFeeDistribution(multiFeeDistribution).getBalances(user);
    return _lockedUsdValue(_balances.locked);
}

function _lockedUsdValue(uint256 lockedLP) internal view returns (uint256) {
    uint256 lpPrice = priceProvider.getLpTokenPriceUsd();
    return (lockedLP * lpPrice) / 10 ** 18;
}
```
Based on the `lockedUsdValue` function and the `_lockedUsdValue()` function, we know that:
```solidity
lockedValue = _lockedUsdValue(_balances.locked) = (_balances.locked * lpPrice) / 10**18;

uint256 requiredValue = (requiredUsdValue(_user) * priceToleranceRatio) / RATIO_DIVISOR;
```
This expands to:
```solidity
requiredValue = _lockedUsdValue((totalNormalDebt * requiredDepositRatio) / RATIO_DIVISOR) * priceToleranceRatio / RATIO_DIVISOR;
```
Which further breaks down to:
```solidity
requiredValue = (((totalNormalDebt * requiredDepositRatio) / RATIO_DIVISOR) * lpPrice / 10**18) * (priceToleranceRatio / RATIO_DIVISOR);
```
This shows the step-by-step calculation of the `lockedValue` and `requiredValue` based on the total debt, deposit ratio, and price tolerances.

Thus, the comparison `lockedValue >= requiredValue` becomes:
```solidity
lockedLP > totalNormalDebt * (requiredDepositRatio / RATIO_DIVISOR) * (priceToleranceRatio / RATIO_DIVISOR)
```
Where:

  * `requiredDepositRatio / RATIO_DIVISOR` = 5%
  * `priceToleranceRatio / RATIO_DIVISOR` = 90%

This simplifies to:
```solidity
lockedLP > totalNormalDebt * 5% * 90% = 4.5% * totalNormalDebt
```
So, the condition checks if the `lockedLP` is greater than 4.5% of the `totalNormalDebt`.

This contradicts the description in the documentation:
> “Loopers maintaining a dLP value exceeding 5% of their Total Position Size qualify for LOOP token emissions to offset borrowing costs incurred from leveraging.”

In reality, because the value of one `lockedLP` token is lower than the value of the debt (in ETH), the number of `lockedLP` tokens falls far short of the actual requirement.

## Recommendation
In the `requiredUsdValue` function, the debt value is first calculated and then multiplied by the relevant ratio. In fact, Radiant Capital implements this exact approach in their code, as shown [here](https://github.com/radiant-capital/v2/blob/cd618877151896415705468f1b2a43c4b75b3c5b/contracts/radiant/eligibility/EligibilityDataProvider.sol#L186).
