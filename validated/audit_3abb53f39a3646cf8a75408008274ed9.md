### Title
ETH Deposit Limit Bypass Due to Missing `amount` in Boundary Check - (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric boundary check: for non-ETH assets it correctly tests `totalAssetDeposits + amount > depositLimit`, but for native ETH it omits the incoming `amount` and only tests `totalAssetDeposits > depositLimit`. This means that when `totalAssetDeposits == depositLimit` (exactly at the cap), the ETH branch returns `false` (not exceeded) and the deposit proceeds, pushing the total above the configured limit.

---

### Finding Description

```solidity
// contracts/LRTDepositPool.sol
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← missing `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // correct
}
``` [1](#0-0) 

The ETH branch evaluates only whether the **current** total already exceeds the limit, not whether the **post-deposit** total would. At the exact boundary (`totalAssetDeposits == depositLimit`), the expression `totalAssetDeposits > depositLimit` evaluates to `false`, so `_beforeDeposit` does not revert with `MaximumDepositLimitReached`, and `depositETH` completes successfully. [2](#0-1) 

The non-ETH path (`depositAsset`) is unaffected because it includes `+ amount` in the comparison. [3](#0-2) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns (deposit cap invariant violated).**

The `depositLimitByAsset` cap is the protocol's primary risk-management control over how much ETH it accepts into EigenLayer restaking. When the cap is exactly reached, any depositor can still push one additional ETH deposit through, minting rsETH beyond the intended ceiling. This breaks the core invariant that `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset(ETH)` at all times. [4](#0-3) 

After the over-deposit, `totalAssetDeposits > depositLimit` becomes `true`, so subsequent ETH deposits are correctly blocked — the cap is exceeded by exactly one deposit amount.

---

### Likelihood Explanation

**Medium.** The condition `totalAssetDeposits == depositLimit` is a natural state the protocol reaches whenever the cap is fully subscribed. Any unprivileged depositor who monitors on-chain state can call `depositETH` at that moment. No special role, front-running, or oracle manipulation is required — only a standard ETH deposit call. [4](#0-3) 

---

### Recommendation

Apply the same `+ amount` term to the ETH branch:

```diff
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
-       return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
+       return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

---

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether` via `LRTConfig.updateAssetDepositLimit`.
2. Depositors fill the pool until `getTotalAssetDeposits(ETH_TOKEN) == 1000 ether`.
3. At this point `getAssetCurrentLimit(ETH_TOKEN)` returns `0` (correctly signals no capacity).
4. Attacker calls `depositETH{value: 50 ether}(0, "")`.
5. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `1000 ether > 1000 ether` → `false` → no revert.
6. `_mintRsETH` mints rsETH for the attacker; `getTotalAssetDeposits(ETH_TOKEN)` is now `1050 ether`, exceeding the cap. [1](#0-0) [5](#0-4)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L399-409)
```text
    /// @notice gets the current limit of asset deposit
    /// @param asset Asset address
    /// @return currentLimit Current limit of asset deposit
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L648-663)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

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
