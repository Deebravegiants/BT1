Audit Report

## Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing One-Deposit Overshoot - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses an asymmetric comparison: the ETH branch tests only `totalAssetDeposits > limit`, omitting the incoming `amount`, while the ERC-20 branch correctly tests `totalAssetDeposits + amount > limit`. This allows any depositor to push ETH TVL above the configured cap by exactly one deposit whenever `totalAssetDeposits` is at or near the limit.

## Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` (L676–682), the ETH branch at L679 returns `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` without including `amount`, while the ERC-20 branch at L681 returns `totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)`.

When `totalAssetDeposits == depositLimit`, the ETH branch evaluates `depositLimit > depositLimit` → `false`, so `_beforeDeposit` (L661–663) does not revert with `MaximumDepositLimitReached`. The call proceeds through `depositETH` (L76–93), which is a public payable function requiring no privileges, and `_mintRsETH` executes, leaving `totalAssetDeposits = depositLimit + msg.value`.

The same state for an ERC-20 deposit would evaluate `depositLimit + amount > depositLimit` → `true` → revert, making the enforcement asymmetric.

## Impact Explanation
The deposit limit is a risk-management invariant set by the admin to cap protocol ETH exposure. The missing `amount` term means the limit can be overshot by up to one full deposit. No funds are stolen or frozen, but the protocol holds more ETH than the operator-configured ceiling. This matches the allowed impact: **Low — Contract fails to deliver promised returns (deposit cap), but does not lose value.**

## Likelihood Explanation
The condition is met whenever `totalAssetDeposits` reaches exactly the configured limit, which is a natural state during normal operation as the cap is approached. Any unprivileged external caller invoking `depositETH` at that moment triggers the overshoot with no special setup, no privileged access, and no victim cooperation required. The condition is repeatable if the limit is raised and approached again.

## Recommendation
Include the incoming `amount` in the ETH branch to match the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets ETH deposit limit to 1000 ETH via `lrtConfig.setDepositLimitByAsset(ETH_TOKEN, 1000e18)`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `1000e18`.
3. Any user calls `depositETH{value: 100 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 100e18)`:
   - `totalAssetDeposits = 1000e18`
   - ETH branch: `1000e18 > 1000e18` → `false` → no revert
5. `_mintRsETH` executes; total ETH deposits become `1100e18` — 10% above the configured cap.
6. Foundry test: deploy pool, set limit to `1000e18`, deposit `1000e18` in setup, then call `depositETH{value: 100e18}` and assert `getTotalAssetDeposits(ETH_TOKEN) == 1100e18` and no revert occurred. Contrast with an ERC-20 deposit at the same state asserting `MaximumDepositLimitReached` revert.