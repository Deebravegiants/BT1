### Title
`LRTDepositPool._beforeDeposit` — Remaining LST Deposit Capacity Becomes Permanently Inaccessible When `depositLimit - totalDeposits < minAmountToDeposit` - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool` enforces both a per-asset deposit ceiling (`depositLimitByAsset`) and a global minimum deposit floor (`minAmountToDeposit`). When the remaining capacity for an LST asset — `depositLimitByAsset[asset] - totalAssetDeposits` — falls below `minAmountToDeposit`, the two checks in `_beforeDeposit` create a mutually exclusive revert condition: any deposit at or above the minimum will exceed the ceiling, and any deposit below the minimum is rejected by the floor. The remaining capacity becomes permanently inaccessible without admin intervention.

---

### Finding Description

`_beforeDeposit` applies two sequential checks for LST deposits:

```solidity
// contracts/LRTDepositPool.sol:657-663
if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
    revert InvalidAmountToDeposit();
}

if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
```

For LST assets, `_checkIfDepositAmountExceedesCurrentLimit` evaluates:

```solidity
// contracts/LRTDepositPool.sol:681
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

When `depositLimitByAsset[asset] - totalAssetDeposits < minAmountToDeposit`:

- Any `depositAmount >= minAmountToDeposit` causes `totalAssetDeposits + depositAmount > depositLimitByAsset` → `MaximumDepositLimitReached`
- Any `depositAmount < minAmountToDeposit` → `InvalidAmountToDeposit`

No valid deposit amount exists. The gap between `totalAssetDeposits` and `depositLimitByAsset` is permanently unreachable through the public `depositAsset` path. [1](#0-0) [2](#0-1) 

---

### Impact Explanation

The deposit pool cannot be filled to its stated limit for the affected LST asset. Any remaining capacity below `minAmountToDeposit` is permanently inaccessible via the public deposit path. This constitutes a **contract failing to deliver its promised returns** (Low): users who wish to deposit are blocked even though the protocol's own accounting shows available capacity (`getAssetCurrentLimit` returns a non-zero value), creating a misleading state. [3](#0-2) 

---

### Likelihood Explanation

`minAmountToDeposit` is a single global value applied to all assets. `depositLimitByAsset` is per-asset and can be set independently. As deposits for a given LST accumulate organically toward the limit, the remaining capacity will eventually fall below `minAmountToDeposit`. No malicious actor is required; normal protocol usage produces this state. The condition is also not self-healing — it persists until an admin either lowers `minAmountToDeposit` or raises `depositLimitByAsset`. [4](#0-3) [5](#0-4) 

---

### Recommendation

In `_beforeDeposit`, when `depositAmount >= minAmountToDeposit` but `totalAssetDeposits + depositAmount > depositLimitByAsset`, accept the deposit capped at the remaining capacity (i.e., `depositAmount = depositLimitByAsset - totalAssetDeposits`) rather than reverting, provided the capped amount is non-zero. Alternatively, enforce at configuration time that `depositLimitByAsset[asset] - currentTotalDeposits >= minAmountToDeposit` whenever either parameter is updated, so the stuck state can never be entered. [6](#0-5) 

---

### Proof of Concept

**Setup:**
- `minAmountToDeposit = 1e18` (1 LST token)
- `depositLimitByAsset[stETH] = 100e18`
- Current `totalAssetDeposits(stETH) = 99.5e18`
- Remaining capacity: `0.5e18`

**Attempt 1 — deposit `1e18` (at minimum):**
```
totalAssetDeposits + 1e18 = 100.5e18 > 100e18  →  MaximumDepositLimitReached
```

**Attempt 2 — deposit `0.5e18` (exactly the remaining capacity):**
```
0.5e18 < minAmountToDeposit (1e18)  →  InvalidAmountToDeposit
```

Both paths revert. `getAssetCurrentLimit(stETH)` still returns `0.5e18`, advertising available capacity that is unreachable. The deposit pool is stuck until an admin adjusts `minAmountToDeposit` or `depositLimitByAsset`. [7](#0-6) [2](#0-1)

### Citations

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L279-285)
```text
    /// @notice update min amount to deposit
    /// @dev only callable by LRT admin
    /// @param minAmountToDeposit_ Minimum amount to deposit
    function setMinAmountToDeposit(uint256 minAmountToDeposit_) external onlyLRTAdmin {
        minAmountToDeposit = minAmountToDeposit_;
        emit MinAmountToDepositUpdated(minAmountToDeposit_);
    }
```

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
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

**File:** contracts/LRTConfig.sol (L123-133)
```text
    function updateAssetDepositLimit(
        address asset,
        uint256 depositLimit
    )
        external
        onlyRole(LRTConstants.MANAGER)
        onlySupportedAsset(asset)
    {
        depositLimitByAsset[asset] = depositLimit;
        emit AssetDepositLimitUpdate(asset, depositLimit);
    }
```
