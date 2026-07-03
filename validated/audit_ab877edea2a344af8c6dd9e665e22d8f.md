Audit Report

## Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Cap Bypass - (File: `contracts/LRTDepositPool.sol`)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses an asymmetric comparison for ETH vs. ERC20 assets: the ETH branch checks only whether the pre-deposit total already exceeds the limit, while the ERC20 branch correctly adds the incoming `amount` before comparing. Any unprivileged depositor can therefore push the protocol's ETH holdings above the configured `depositLimitByAsset` cap in a single transaction, violating the protocol's deposit ceiling invariant.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, `_checkIfDepositAmountExceedesCurrentLimit` contains:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));       // ← missing + amount
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));  // ← correct
```

The ETH branch returns `true` (reject) only when the current aggregate already exceeds the limit. It never factors in the incoming `amount`. The ERC20 branch correctly computes the post-deposit total before comparing.

This function is the sole guard called from `_beforeDeposit` (lines 648–670), which is itself the only check in `depositETH` (lines 76–93). There are no other deposit-limit checks in the ETH deposit path. When `totalAssetDeposits == depositLimit - 1 wei`, the ETH check returns `false` regardless of how large `amount` is, and the deposit proceeds unconstrained.

## Impact Explanation
The deposit limit (`depositLimitByAsset`) is the protocol's primary risk-management cap on ETH exposure. Because the ETH branch ignores `amount`, the cap is never enforced prospectively — it only triggers after the limit has already been exceeded by a prior deposit. Any depositor can mint rsETH against ETH that exceeds the intended ceiling. This matches the allowed impact class **Low: Contract fails to deliver promised returns** — the deposit cap is a documented protocol guarantee that is silently not upheld for ETH.

## Likelihood Explanation
`depositETH` is `external payable` with no role restriction. The only precondition is that `totalAssetDeposits` is at or below the limit, which is the normal operating state of the protocol. No front-running, oracle manipulation, or privileged access is required. Any user with ETH can trigger this in a single transaction, and it is repeatable indefinitely.

## Recommendation
Add `amount` to the ETH branch to match the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 100 ether`.
2. `getTotalAssetDeposits(ETH_TOKEN)` returns `99 ether`.
3. Attacker calls `depositETH{value: 50 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 50 ether)` evaluates `99 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` executes; protocol now holds 149 ETH — 49 ETH above the cap.
6. Repeat with any `amount` while `totalAssetDeposits ≤ depositLimit`.

**Foundry test plan:**
```solidity
function test_ethDepositBypassesLimit() public {
    vm.prank(admin);
    lrtConfig.setDepositLimitByAsset(ETH_TOKEN, 100 ether);
    // seed 99 ether via prior deposits
    _seedETHDeposits(99 ether);
    // attacker deposits 50 ether — should revert but does not
    vm.deal(attacker, 50 ether);
    vm.prank(attacker);
    lrtDepositPool.depositETH{value: 50 ether}(0, "");
    // assert total exceeds limit
    assertGt(lrtDepositPool.getTotalAssetDeposits(ETH_TOKEN), 100 ether);
}
```