Audit Report

## Title
ETH Deposit Cap Check Omits New Deposit Amount, Allowing Cap Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric cap check: the ETH branch evaluates only `totalAssetDeposits > depositLimit`, ignoring the incoming `amount`, while the ERC20 branch correctly evaluates `totalAssetDeposits + amount > depositLimit`. Any single ETH deposit that would push the running total over the configured cap is silently accepted, breaking the deposit-limit invariant.

## Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` (L676–682), the ETH branch returns `(totalAssetDeposits > lrtConfig.depositLimitByAsset(asset))` without including `amount`, even though `amount` is the function parameter representing the incoming deposit value. [1](#0-0) 

The public entry point `depositETH` passes `msg.value` as `depositAmount` to `_beforeDeposit`: [2](#0-1) 

`_beforeDeposit` forwards it to the cap check: [3](#0-2) 

Because the ETH branch never adds `amount` to `totalAssetDeposits`, any deposit where `totalAssetDeposits ≤ depositLimit` passes the check regardless of how large `msg.value` is. The ERC20 path at L681 does not share this flaw.

## Impact Explanation
The deposit cap (`lrtConfig.depositLimitByAsset(ETH_TOKEN)`) is a protocol-level risk control. Its bypass allows total ETH holdings to exceed the configured limit in a single transaction, causing the protocol to mint more rsETH than the cap was designed to permit. This breaks the invariant `totalETHDeposits ≤ depositLimitByAsset` and constitutes **Low — Contract fails to deliver promised returns**, matching the allowed impact scope.

## Likelihood Explanation
`depositETH` is a public, permissionless, payable function requiring no special role. The only precondition is that `totalAssetDeposits` is currently below the cap, which is the normal operating state. Any user with sufficient ETH can trigger this in a single transaction, making it trivially reachable and repeatable until the cap is manually raised or the function is paused.

## Recommendation
Remove the special-case ETH branch and apply the same `+ amount` logic uniformly:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This unifies the check and ensures the incoming deposit is always counted before comparing against the limit.

## Proof of Concept
1. Deploy with `depositLimitByAsset(ETH_TOKEN) = 100 ether`; seed `getTotalAssetDeposits(ETH_TOKEN) = 99 ether`.
2. Call `depositETH{value: 50 ether}(0, "")`.
3. Inside `_checkIfDepositAmountExceedesCurrentLimit`: ETH branch evaluates `99 ether > 100 ether` → `false` → cap check passes; the `50 ether` argument is never used.
4. `_mintRsETH` executes; contract now holds `149 ether`, 49 ETH above the cap.
5. Foundry invariant test: assert `getTotalAssetDeposits(ETH_TOKEN) ≤ lrtConfig.depositLimitByAsset(ETH_TOKEN)` after any sequence of `depositETH` calls — the invariant will be violated by step 4.

### Citations

**File:** contracts/LRTDepositPool.sol (L87-87)
```text
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
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
