Audit Report

## Title
ETH Deposit Limit Bypass via Missing `amount` in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses asymmetric logic: the ERC20 branch correctly checks `totalAssetDeposits + amount > limit`, but the ETH branch checks only `totalAssetDeposits > limit`, omitting the incoming deposit `amount`. As a result, the ETH deposit cap is never enforced against the size of the incoming deposit, allowing any depositor to push total ETH deposits past the admin-configured limit in a single transaction.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount not included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The ETH branch at line 679 evaluates only the pre-deposit running total against the cap. The `amount` parameter (which carries `msg.value` from `depositETH`) is silently ignored. The function therefore returns `false` ("limit not exceeded") whenever the running total has not yet crossed the cap, regardless of how large the incoming deposit is.

The call chain is:
- `depositETH` (line 87) → `_beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, ...)` (line 661) → `_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)` — if this returns `false`, no revert occurs and the deposit proceeds.

`depositETH` is a public `payable` function with no role restriction, so any depositor can trigger this path.

## Impact Explanation
The ETH deposit limit (`depositLimitByAsset`) is a protocol-level risk-management cap controlling how much ETH can be restaked into EigenLayer strategies. Because the cap is not enforced against the size of the incoming ETH deposit, any depositor can push total ETH deposits arbitrarily above the configured limit in a single transaction. This breaks the protocol's stated deposit ceiling without any direct fund theft. This matches the allowed impact: **Low — Contract fails to deliver promised returns**.

## Likelihood Explanation
The entry point is `depositETH`, a public `payable` function with no access control. The condition is trivially reachable whenever `totalAssetDeposits` is below the configured limit (the normal operating state). No special privileges, victim mistakes, or external conditions are required. Any depositor can exploit this repeatedly.

## Recommendation
Add `amount` to the ETH branch to match the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets ETH deposit limit to 1,000 ETH via `lrtConfig.depositLimitByAsset(ETH_TOKEN)`.
2. `getTotalAssetDeposits(ETH_TOKEN)` returns 999 ETH.
3. Attacker calls `depositETH{value: 10 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999 ETH > 1000 ETH` → `false` → no revert.
5. Deposit succeeds; total ETH deposits become 1,009 ETH — 9 ETH above the configured cap.

**Foundry test sketch:**
```solidity
function test_ethLimitBypass() public {
    // set limit to 1000 ether
    lrtConfig.setDepositLimitByAsset(ETH_TOKEN, 1000 ether);
    // bring total to 999 ether via prior deposits
    // ...
    // single deposit of 10 ether should revert but does not
    vm.deal(attacker, 10 ether);
    vm.prank(attacker);
    lrtDepositPool.depositETH{value: 10 ether}(0, "");
    assertGt(lrtDepositPool.getTotalAssetDeposits(ETH_TOKEN), 1000 ether);
}
```