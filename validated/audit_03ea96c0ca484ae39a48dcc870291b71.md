Audit Report

## Title
ETH Deposit Limit Check Excludes New Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric deposit-cap check: the ETH branch compares only `totalAssetDeposits > limit`, omitting the incoming `amount`, while the ERC-20 branch correctly evaluates `totalAssetDeposits + amount > limit`. Any depositor can therefore push ETH holdings above the governance-approved ceiling, minting rsETH beyond the intended maximum supply.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the function branches on `asset == LRTConstants.ETH_TOKEN`:

```solidity
// L678-681
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount omitted
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // amount included
```

When `totalAssetDeposits == depositLimitByAsset`, the ETH check evaluates `limit > limit` → `false`, so `_beforeDeposit` (L661) does not revert with `MaximumDepositLimitReached`. The caller's full `msg.value` is accepted, `_mintRsETH` is called (L90), and `totalAssetDeposits` rises above the cap. The ERC-20 path is unaffected. The call chain is: `depositETH` (L76) → `_beforeDeposit` (L648) → `_checkIfDepositAmountExceedesCurrentLimit` (L676).

## Impact Explanation
The deposit limit is a governance-enforced risk-management ceiling. Bypassing it for ETH allows the protocol to accept unbounded ETH beyond the approved cap, inflating rsETH supply past the intended maximum. This matches **Low – contract fails to deliver promised returns (the deposit cap guarantee), but does not directly lose user value**.

## Likelihood Explanation
No special role or privilege is required. The condition is met naturally as the pool fills to its cap. Any unprivileged external caller invoking `depositETH` at the moment `totalAssetDeposits == depositLimitByAsset` can exploit this. The exploit is repeatable on every subsequent deposit once the cap is reached.

## Recommendation
Mirror the ERC-20 logic in the ETH branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Pool accumulates `totalAssetDeposits = 100 ether` (exactly at cap).
3. Attacker calls `depositETH{value: 50 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `100 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 50 ETH; `getTotalAssetDeposits(ETH_TOKEN)` returns `150 ether`, 50% above the cap.

**Foundry test sketch:**
```solidity
function test_ethDepositLimitBypass() public {
    vm.prank(admin);
    lrtConfig.setDepositLimitByAsset(ETH_TOKEN, 100 ether);
    // fill pool to exactly the cap
    depositor.depositETH{value: 100 ether}(0, "");
    // this should revert but does not
    attacker.depositETH{value: 50 ether}(0, "");
    assertGt(depositPool.getTotalAssetDeposits(ETH_TOKEN), 100 ether);
}
```