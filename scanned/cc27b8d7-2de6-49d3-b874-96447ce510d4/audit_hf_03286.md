# [M] `syncFeeCheckpoint`

## Summary
Severity: Medium
Contest weight: 0.7206
Dataset id: 18045
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the syncFeeCheckpoint modifier of the Vault contract. The modifier is intended to update the highWaterMark, a stored reference share value used to determine whether performance fees should be charged. Instead of only raising the highWaterMark when the current share value exceeds the previous one, the code unconditionally assigns highWaterMark = convertToAssets(1e18). Consequently, whenever a function protected by the modifier (such as deposit or withdraw) executes, the stored highWaterMark can be lowered if the share price has fallen. This regression causes the subsequent fee calculation in accruedPerformanceFee to see shareValue > highWaterMark even when the share price has not truly increased, leading to performance fees being minted erroneously. The impact is that investors may see a reduction in their net balance or receive fewer shares than expected, effectively paying fees on stagnant or decreasing asset values. The condition occurs each time the syncFeeCheckpoint modifier runs, which is after every deposit, withdrawal, or any operation that includes the modifier. The affected parties are the vault users and the protocol’s fee recipient, as the protocol may collect more fees than justified. The issue was identified during a formal audit when reviewers examined the modifier’s logic and observed that it does not guard against decreasing the highWaterMark. The bug is subtle because the fee overcharge can be small and may be attributed to normal fee accrual, making it difficult to detect without inspecting the state changes. The proper fix is to change the modifier so that it only updates highWaterMark when the newly computed share value is greater than the stored value, preserving the invariant that highWaterMark never decreases. This aligns the fee calculation with the intended accounting model where performance fees are charged only on genuine profit above the previous peak. In user‑facing terms, a depositor may notice that after a deposit the reported share price drops and that later fee deductions appear even though the vault’s value has not risen, contradicting the expectation that fees are taken only on gains.

## Proof of Concept
The `Vault.syncFeeCheckpoint()` function does not modify the `highWaterMark` correctly, sometimes it might even decrease its value, resulting in charging more performance fees than it should. Instead of updating with a higher share values, it might actually decrease the value of `highWaterMark`. As a result, more performance fees might be charged since the `highWaterMark` was brought down again and again.

[https://github.com/code-423n4/2023-01-popcorn/blob/d95fc31449c260901811196d617366d6352258cd/src/vault/Vault.sol#L496-L499](https://github.com/code-423n4/2023-01-popcorn/blob/d95fc31449c260901811196d617366d6352258cd/src/vault/Vault.sol#L496-L499)

```solidity
     modifier syncFeeCheckpoint() {
            _;
            highWaterMark = convertToAssets(1e18);
        }
```

  1. Suppose the current `highWaterMark = 2 * e18` and `convertToAssets(1e18) = 1.5 * e18`.
  2. After `deposit()` is called, since the `deposit()` function has the `synFeeCheckpoint` modifier, the `highWaterMark` will be incorrectly reset to `1.5 * e18`.
  3. Suppose after some activities, `convertToAssets(1e18) = 1.99 * e18`.
  4. `TakeFees()` is called, then the performance fee will be charged, since it wrongly decides `convertToAssets(1e18) > highWaterMark` with the wrong `highWaterMark = 1.5 * e18`. The correct `highWaterMark` should be `2 * e18`:

```solidity
     modifier takeFees() {
            uint256 managementFee = accruedManagementFee();
            uint256 totalFee = managementFee + accruedPerformanceFee();
            uint256 currentAssets = totalAssets();
            uint256 shareValue = convertToAssets(1e18);

            if (shareValue > highWaterMark) highWaterMark = shareValue;

            if (managementFee > 0) feesUpdatedAt = block.timestamp;

            if (totalFee > 0 && currentAssets > 0)
                _mint(feeRecipient, convertToShares(totalFee));

            _;
        }
    function accruedPerformanceFee() public view returns (uint256) {
            uint256 highWaterMark_ = highWaterMark;
            uint256 shareValue = convertToAssets(1e18);
            uint256 performanceFee = fees.performance;

            return
                performanceFee > 0 && shareValue > highWaterMark
                    ? performanceFee.mulDiv(
                        (shareValue - highWaterMark) * totalSupply(),
                        1e36,
                        Math.Rounding.Down
                    )
                    : 0;
        }
```

  5. As a result, the performance fee is charged when it is not supposed to do so. Investors might not be happy with this.

## Recommendation
Revise the `syncFeeCheckpoint()` as follows:

```solidity
     modifier syncFeeCheckpoint() {
            _;

             uint256 shareValue = convertToAssets(1e18);

            if (shareValue > highWaterMark) highWaterMark = shareValue;
        }
```
