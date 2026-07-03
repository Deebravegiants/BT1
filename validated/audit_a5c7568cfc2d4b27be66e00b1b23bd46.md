Audit Report

## Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Deposits to Exceed the Configured Cap — (File: `contracts/LRTDepositPool.sol`)

## Summary

`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool` applies an asymmetric comparison: for LST assets it correctly evaluates `totalAssetDeposits + amount > limit`, but for ETH it evaluates only `totalAssetDeposits > limit`, omitting the incoming `amount`. As a result, any depositor can push total ETH deposits above the admin-configured cap in a single `depositETH` call, violating the deposit-limit invariant the protocol is meant to enforce.

## Finding Description

The root cause is in `_checkIfDepositAmountExceedesCurrentLimit` at lines 676–682 of `contracts/LRTDepositPool.sol`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount not included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
``` [1](#0-0) 

The ETH branch only returns `true` (triggering a revert) if the limit was **already** exceeded before the deposit. When `totalAssetDeposits <= depositLimit`, the check always returns `false` regardless of `amount`, so any `msg.value` is accepted.

The call path is: `depositETH` (line 87) → `_beforeDeposit` (line 661) → `_checkIfDepositAmountExceedesCurrentLimit`. There is no secondary ETH cap enforcement anywhere else in the deposit path. [2](#0-1) [3](#0-2) 

## Impact Explanation

The ETH deposit limit is a safety parameter set by the `MANAGER` role to bound the protocol's ETH exposure. Bypassing it means the protocol silently accepts more ETH than the configured ceiling. No funds are directly stolen, but the protocol fails to deliver the promised deposit-cap guarantee.

**Impact: Low — Contract fails to deliver promised returns.**

## Likelihood Explanation

The precondition is the normal operating state of the protocol: `totalAssetDeposits <= depositLimit`. Any unprivileged caller of `depositETH` can trigger this without any special role, front-running, or unusual state. The condition is trivially and repeatably reachable.

**Likelihood: High.**

## Recommendation

Add `amount` to the ETH branch to mirror the LST branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept

1. Admin sets ETH deposit limit to 1,000 ETH via `updateAssetDepositLimit`.
2. Protocol accumulates 999.9 ETH across the pool, NDCs, and EigenLayer (`getTotalAssetDeposits(ETH_TOKEN)` returns 999.9 ETH).
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999.9 ETH > 1000 ETH` → `false` → no revert.
5. 500 ETH is accepted; total ETH deposits become 1,499.9 ETH — 50% above the configured cap.
6. The limit is now permanently exceeded; subsequent honest depositors are blocked while the attacker's over-deposit remains in the protocol.

**Foundry test plan:** Deploy `LRTDepositPool` with a mock config setting ETH limit to 1,000 ether. Pre-fund the pool to 999.9 ether. Call `depositETH{value: 500 ether}` from an unprivileged address. Assert the call succeeds and `getTotalAssetDeposits(ETH_TOKEN)` returns a value greater than 1,000 ether.

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
