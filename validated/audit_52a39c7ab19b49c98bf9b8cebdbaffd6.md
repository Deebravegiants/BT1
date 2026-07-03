Audit Report

## Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Cap Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses `totalAssetDeposits > depositLimit` for ETH but `totalAssetDeposits + amount > depositLimit` for ERC-20 assets. The missing `amount` in the ETH branch means any depositor can push the ETH total above the configured cap in a single call. No funds are stolen, but the protocol mints rsETH beyond the intended ceiling.

## Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` (L676–682), the ETH branch at L679 returns `true` only when the *current* total already exceeds the limit, ignoring the incoming `amount`:

```solidity
// L678-679: ETH — amount excluded
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
// L681: ERC-20 — amount correctly included
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

`_beforeDeposit` (L648–670) calls this check at L661–663 and reverts on `true`. Because the ETH path never adds `amount`, the check returns `false` (allow) whenever `totalAssetDeposits <= depositLimit`, regardless of how large `amount` is. The call chain is: `depositETH` (L76) → `_beforeDeposit` (L648) → `_checkIfDepositAmountExceedesCurrentLimit` (L676) → `_mintRsETH` (L686). No other guard in `_beforeDeposit` or `depositETH` enforces the cap.

## Impact Explanation
The ETH deposit cap is a protocol-level safety ceiling. Because the incoming `amount` is excluded from the ETH comparison, any unprivileged depositor can exceed that ceiling in a single `depositETH` call. The protocol mints rsETH for the excess ETH and the cap is permanently overshot. This matches the allowed Low impact: **Contract fails to deliver promised returns** (deposit limit not enforced for ETH).

## Likelihood Explanation
`depositETH` is a public `payable` function requiring no special role, no front-running, and no external dependency. The condition is met naturally whenever the ETH pool approaches its configured limit, which is a normal operational state. Any user can trigger it with a sufficiently large `msg.value`.

## Recommendation
Add `amount` to the ETH comparison to match the ERC-20 path:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `1000 ether`.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `1000 ether > 1000 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 500 ETH; total ETH in protocol is now `1500 ether`, 50% above the cap.
6. The equivalent ERC-20 call evaluates `1000 + 500 > 1000` → `true` → reverts correctly.

**Foundry test plan:**
```solidity
function test_ethDepositBypassesCap() public {
    vm.deal(attacker, 500 ether);
    // fill pool to exactly the limit via prior deposits
    // assert getTotalAssetDeposits(ETH_TOKEN) == depositLimit
    vm.prank(attacker);
    depositPool.depositETH{value: 500 ether}(0, "");
    // assert getTotalAssetDeposits(ETH_TOKEN) == depositLimit + 500 ether
    // assert no revert occurred
}
```