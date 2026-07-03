### Title
ETH Deposit Limit Check Excludes Current Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an inconsistent limit check between ETH and ERC20 assets. For ERC20 tokens the check correctly includes the incoming deposit amount (`totalAssetDeposits + amount > limit`), but for ETH it omits `amount` entirely (`totalAssetDeposits > limit`). This means any user can deposit ETH when the running total is exactly at the configured limit, pushing the protocol past its own cap.

---

### Finding Description

In `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// contracts/LRTDepositPool.sol L676-L682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount excluded
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
```

The ETH branch uses a strict `>` comparison against `depositLimitByAsset` **without adding `amount`**. When `totalAssetDeposits == depositLimit` the expression evaluates to `false`, so `_beforeDeposit` does not revert and the deposit is accepted. After the call completes, `address(this).balance` (and therefore `getTotalAssetDeposits(ETH_TOKEN)`) exceeds the configured limit by exactly `msg.value`.

The ERC20 path does not share this flaw: `totalAssetDeposits + amount > limit` correctly blocks a deposit that would breach the cap.

This is called from `_beforeDeposit` (L661), which is the sole pre-flight guard for both `depositETH` (L87) and `depositAsset` (L111). The public entry point `depositETH` is callable by any unprivileged user. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

The ETH deposit limit (`depositLimitByAsset[ETH_TOKEN]`) is the protocol's primary risk-management cap on native ETH exposure to EigenLayer. Bypassing it allows the protocol to accept more ETH than the governance-approved ceiling, violating the invariant the limit is meant to enforce. No funds are directly stolen, but the protocol delivers less than its promised safety guarantee.

**Impact: Low** — Contract fails to deliver promised returns (deposit cap enforcement), but does not lose value.

---

### Likelihood Explanation

The condition is reached naturally as the protocol fills up: once cumulative ETH deposits equal `depositLimitByAsset[ETH_TOKEN]`, the very next `depositETH` call from any user will bypass the check. No special privileges, flash loans, or coordination are required. The entry path is fully permissionless.

---

### Recommendation

Include `amount` in the ETH branch, matching the ERC20 logic:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    // unified check for both ETH and ERC20
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

---

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 10_000 ether` via `LRTConfig.updateAssetDepositLimit`.
2. Over time, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `10_000 ether`.
3. Alice calls `depositETH{value: 1 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit`:
   - `totalAssetDeposits = 10_000 ether`
   - ETH branch: `10_000 ether > 10_000 ether` → `false` → no revert.
5. `_mintRsETH` executes; Alice receives rsETH.
6. `getTotalAssetDeposits(ETH_TOKEN)` is now `10_001 ether`, exceeding the limit.
7. Any subsequent depositor can repeat step 3 until the check finally triggers (`totalAssetDeposits > limit`), meaning the protocol can absorb up to `limit + maxSingleDeposit` before the guard activates. [4](#0-3) [5](#0-4)

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
