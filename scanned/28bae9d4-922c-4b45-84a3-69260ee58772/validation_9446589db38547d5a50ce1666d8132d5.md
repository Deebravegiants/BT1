### Title
Attacker Can Inflate Deposit Pool Balance via Direct Token Transfer to Permanently Block All User Deposits - (File: `contracts/LRTDepositPool.sol`)

---

### Summary

`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` relies on `getTotalAssetDeposits`, which uses the raw `IERC20(asset).balanceOf(address(this))` of the pool. Any unprivileged actor can directly transfer a supported LST to the `LRTDepositPool` contract address, inflating the tracked total above `depositLimitByAsset`, and causing every subsequent `depositAsset` call for that asset to revert with `MaximumDepositLimitReached`.

---

### Finding Description

`depositAsset` calls `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit`: [1](#0-0) 

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    ...
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

`getTotalAssetDeposits` aggregates via `getAssetDistributionData`: [2](#0-1) 

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

This is the **raw ERC20 balance** of the contract. Because `LRTDepositPool` has no mechanism to distinguish tokens deposited through `depositAsset` from tokens sent directly to the contract address, any direct ERC20 transfer inflates `totalAssetDeposits` one-for-one.

The same issue applies to ETH deposits, where `getETHDistributionData` uses: [3](#0-2) 

```solidity
ethLyingInDepositPool = address(this).balance;
```

and the contract has an open `receive()` payable fallback: [4](#0-3) 

The deposit limit check in `_beforeDeposit` then reverts: [5](#0-4) 

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
```

The analog to the external report is exact: the external vulnerability uses `balance != expected_balance` (equality check manipulated by dust); here the check is `totalAssetDeposits + amount > depositLimit` (threshold check manipulated by direct transfer). In both cases, an unprivileged actor manipulates a raw balance that feeds a critical gate, blocking legitimate user operations.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

All `depositAsset` (and `depositETH`) calls for the targeted asset revert with `MaximumDepositLimitReached` until the LRT manager raises `depositLimitByAsset`. Users cannot enter the protocol for the affected asset during this window. The attacker forfeits the transferred tokens (they receive no rsETH), but the cost is bounded by the remaining headroom under the deposit cap, which can be small when the cap is nearly full.

---

### Likelihood Explanation

**Low–Medium.** The attack requires no special role, no front-running, and no complex setup — a single ERC20 `transfer` call suffices. The economic cost (forfeited tokens) is the primary deterrent. When the deposit cap is nearly exhausted (a common operational state), the cost to tip it over is minimal. The attack is repeatable: each time the manager raises the limit, the attacker can re-tip it.

---

### Recommendation

Replace raw `balanceOf` accounting with an internal deposit ledger. Track only tokens that enter through `depositAsset` / `depositETH` in a storage variable (e.g., `internalBalance[asset]`), and use that variable in `getAssetDistributionData` instead of `IERC20(asset).balanceOf(address(this))`. Tokens sent directly to the contract would then not affect the deposit limit check.

---

### Proof of Concept

1. Observe that `getTotalAssetDeposits(stETH)` returns a value close to `lrtConfig.depositLimitByAsset(stETH)`, say `limit - 1 wei`.
2. Attacker calls `stETH.transfer(address(lrtDepositPool), 1 wei)` directly (no protocol interaction needed).
3. `getAssetDistributionData(stETH)` now returns `assetLyingInDepositPool` inflated by `1 wei`, pushing `totalAssetDeposits` to exactly `limit`.
4. Any user calling `depositAsset(stETH, amount, ...)` hits `_checkIfDepositAmountExceedesCurrentLimit` → `totalAssetDeposits + amount > limit` → `revert MaximumDepositLimitReached()`.
5. All stETH deposits are frozen until the manager calls `updateAssetDepositLimit` to raise the cap.
6. Attacker can repeat step 2 immediately after each manager intervention, sustaining the freeze at negligible marginal cost.

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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
