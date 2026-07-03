Audit Report

## Title
ETH Deposit Limit Check Ignores Deposit Amount, Allowing Limit Overshoot - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` evaluates the ETH deposit limit using only `totalAssetDeposits > depositLimit`, omitting the incoming `amount`. The ERC20 branch correctly uses `totalAssetDeposits + amount > depositLimit`. As a result, when total ETH deposits equal the configured limit, the check returns `false` and the deposit proceeds, pushing total deposits above the cap.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the ETH branch of `_checkIfDepositAmountExceedesCurrentLimit` discards the `amount` parameter:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // amount unused
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // correct
}
```

This function is called at line 661 from `_beforeDeposit`, which gates the `revert MaximumDepositLimitReached()` at line 662. `_beforeDeposit` is invoked by the public `depositETH` at line 87 with `msg.value` as the deposit amount. Because the ETH branch never adds `amount` to `totalAssetDeposits`, the guard only triggers when the limit is already exceeded before the deposit — not when the incoming deposit would cause the overshoot. A depositor whose transaction brings `totalAssetDeposits` from exactly at the limit to above it will never be rejected.

## Impact Explanation
The deposit limit is a risk-management control capping protocol exposure to EigenLayer strategies. The broken check allows any single ETH deposit to push total ETH deposits above the configured cap. No funds are lost, but the protocol fails to enforce its own deposit ceiling. This matches the allowed impact: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

## Likelihood Explanation
The vulnerable path is the public, permissionless `depositETH` function. No privileged role is required. The condition is reachable whenever `totalAssetDeposits(ETH) >= depositLimitByAsset(ETH)`, which is a normal operational state as the protocol fills up. Any ETH depositor can trigger this in a single transaction.

## Recommendation
Add `amount` to the ETH branch to match the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Protocol accumulates `totalAssetDeposits(ETH) = 1000 ether` through normal usage.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `1000 ether > 1000 ether` → `false`.
5. `_beforeDeposit` does not revert; deposit succeeds.
6. `totalAssetDeposits(ETH)` becomes 1500 ether — 50% above the configured limit.
7. The identical scenario with any ERC20 evaluates `1000 + 500 > 1000` → `true` → reverts with `MaximumDepositLimitReached`.

**Foundry test plan:** Deploy `LRTDepositPool` with a mock `lrtConfig` returning `depositLimitByAsset = 1000 ether`. Seed `totalAssetDeposits` to 1000 ether. Call `depositETH{value: 1 ether}` and assert it does not revert. Then assert `getTotalAssetDeposits(ETH_TOKEN) > depositLimitByAsset(ETH_TOKEN)`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L86-93)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```
