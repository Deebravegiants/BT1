### Title
ETH Deposit Limit Bypass Due to Missing Incoming Amount in Limit Check - (File: `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies two structurally different conditions depending on the asset type. For ERC20 tokens it correctly adds the incoming deposit amount to the running total before comparing against the cap. For ETH it omits the incoming amount entirely, checking only whether the existing total already exceeds the cap. This mirrors the external report's root cause: a state-changing operation (here, the deposit itself) proceeds unconditionally when it should be gated by a condition that includes the new value.

---

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` is the sole guard that enforces per-asset deposit caps before rsETH is minted:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount excluded
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
``` [1](#0-0) 

For ERC20 assets the guard is `totalAssetDeposits + amount > limit`, which correctly blocks any deposit that would push the total over the cap.

For ETH the guard is `totalAssetDeposits > limit`, which only blocks deposits when the cap has **already been exceeded**. Any deposit made while `totalAssetDeposits ≤ limit` passes the check regardless of how large `msg.value` is, and the cap is silently breached.

The function is called unconditionally from `_beforeDeposit`, which is the only pre-deposit validation path for both `depositETH` and `depositAsset`:

```solidity
// contracts/LRTDepositPool.sol  lines 648-670
function _beforeDeposit(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected)
    private view returns (uint256 rsethAmountToMint)
{
    ...
    if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
        revert MaximumDepositLimitReached();
    }
    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    ...
}
``` [2](#0-1) 

Because the ETH branch never adds `amount` to the comparison, a depositor can call `depositETH` with an arbitrarily large `msg.value` the moment `totalAssetDeposits ≤ limit`, and the full amount is accepted and minted as rsETH.

---

### Impact Explanation

The ETH deposit cap (`depositLimitByAsset[ETH_TOKEN]`) is not enforced for the incoming deposit amount. Any unprivileged depositor can push the protocol's ETH TVL above the configured limit in a single transaction. Because rsETH is minted proportionally to the deposited ETH value, this results in more rsETH being issued than the protocol's risk parameters allow. The deposit limit is the only on-chain mechanism preventing over-exposure to ETH; its failure means the protocol does not deliver the promised constraint.

**Impact:** Low — contract fails to deliver promised returns (deposit cap enforcement), but no direct loss of user funds occurs.

---

### Likelihood Explanation

The condition is trivially reachable by any ETH depositor at any time the running total is at or below the cap. No special role, timing, or front-running is required. The depositor simply calls `depositETH{value: largeAmount}()` when `totalAssetDeposits ≤ limit`.

---

### Recommendation

Include the incoming ETH amount in the comparison, matching the ERC20 branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← add amount
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Existing deposits accumulate to exactly `100 ether` (`totalAssetDeposits == limit`).
3. Attacker calls `depositETH{value: 50 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `100 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for the full 50 ETH.
6. Protocol now holds 150 ETH against a 100 ETH cap; the limit is exceeded by 50 ETH and the corresponding rsETH has been issued. [1](#0-0) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L86-92)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
```

**File:** contracts/LRTDepositPool.sol (L648-670)
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

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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
