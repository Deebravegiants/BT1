# [M] `ReaperBaseStrategyv4.harvest`

## Summary
Severity: Medium
Contest weight: 0.6240
Dataset id: 18112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ReaperBaseStrategyv4.harvest contains a state‑handling edge case that can cause the function to revert when the strategy holds no active position on the Aave lending pool. The root cause is that the internal withdrawal routine `_withdrawUnderlying` forwards the requested amount directly to the Aave pool without first verifying that the amount is non‑zero. Aave’s `validateWithdraw` function explicitly rejects a withdrawal of zero by reverting with `VL_INVALID_AMOUNT`. When the strategy’s position has been fully withdrawn, `balanceOfPool()` returns zero, the calculated `_withdrawAmount` becomes zero, and the subsequent call to `ILendingPool.withdraw` triggers the Aave revert. In emergency mode, `harvest()` attempts to liquidate all positions, which in this scenario are already zero, leading to the same revert. Because the revert occurs before any state changes, the strategy remains in a “debt” state where it reports a negative balance but still holds some underlying tokens in its contract balance. Consequently, any user‑initiated `withdraw()` also reverts, preventing the owner or a strategist from extracting the remaining tokens. From the user’s point of view the UI may show a pending withdrawal or a zero balance while the transaction fails with an out‑of‑gas or custom error, giving the impression that funds have disappeared. The issue was discovered during a manual audit that simulated an emergency harvest after a full unwind of the Aave position. It is subtle because the code path is only exercised when the pool balance is exactly zero, a condition that does not occur in normal operation, and the revert message originates from an external library, making it easy to overlook. The vulnerability belongs to the class of “zero‑amount external call” bugs, where a contract assumes that a downstream protocol will accept a zero value, violating the accounting assumption that a withdrawal of zero is a no‑op. The recommended fix is to guard the withdrawal call with a condition that skips the external call when the amount is zero, or to adjust the logic so that emergency harvest does not attempt a withdrawal when there is no position. By ensuring that only positive amounts are sent to the lending pool, the strategy can correctly report its state and allow users to retrieve their funds even after an emergency unwind.

## Proof of Concept
The main problem is that [Aave lending pool doesn’t allow 0 withdrawals](https://github.com/aave/protocol-v2/blob/554a2ed7ca4b3565e2ceaea0c454e5a70b3a2b41/contracts/protocol/libraries/logic/ValidationLogic.sol#L60-L70).

```solidity
    function validateWithdraw(
        address reserveAddress,
        uint256 amount,
        uint256 userBalance,
        mapping(address => DataTypes.ReserveData) storage reservesData,
        DataTypes.UserConfigurationMap storage userConfig,
        mapping(uint256 => address) storage reserves,
        uint256 reservesCount,
        address oracle
    ) external view {
        require(amount != 0, Errors.VL_INVALID_AMOUNT);
```

So the below scenario would be possible.

  1. After depositing and withdrawing from the Aave lending pool, the current position is 0 and the strategy is in debt.
  2. It’s possible that the strategy has some want balance in the contract but no position on the lending pool. It’s because `_adjustPosition()` remains the debt during reinvesting and also, there is an `authorizedWithdrawUnderlying()` for `STRATEGIST` to withdraw from the lending pool.
  3. If the strategy is in an emergency, `harvest()` tries to liquidate all positions(=0 actually) and it will revert because of 0 withdrawal from Aave.
  4. Also, `withdraw()` will revert at [L98](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/abstract/ReaperBaseStrategyv4.sol#L98) as the strategy is in the debt.

As a result, the funds might be locked inside the strategy unless the `emergency` mode is canceled.

## Recommendation
We should check 0 withdrawal in `_withdrawUnderlying()`.

```solidity
    function _withdrawUnderlying(uint256 _withdrawAmount) internal {
        uint256 withdrawable = balanceOfPool();
        _withdrawAmount = MathUpgradeable.min(_withdrawAmount, withdrawable);

        if(_withdrawAmount != 0) {
            ILendingPool(ADDRESSES_PROVIDER.getLendingPool()).withdraw(address(want), _withdrawAmount, address(this));
        }
    }
```

Very interesting edge case.

Valid edge case in as far as harvests would fail. However, funds won’t get locked in the strategy. They can still be withdrawn through an appropriate withdraw() TX. Recommend downgrading to low since this is purely about state handling without putting any assets at risk. See screenshot below for simulation:

![Screenshot from 2023-03-14 12-28-48](https://user-images.githubusercontent.com/95557476/225072825-2dbabf26-b6b9-44ff-b5d4-add9c2d0948d.png)

Medium severity is also appropriate when core functionality is impaired, even if there is no lasting damage.
