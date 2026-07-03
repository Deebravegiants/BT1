### Title
ETH Deposit Limit Bypass Due to Asymmetric Check in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

---

### Summary

The `_checkIfDepositAmountExceedesCurrentLimit` function in `LRTDepositPool` applies different comparison logic for ETH versus ERC20 assets. For ETH, the incoming deposit `amount` is silently ignored in the limit check, allowing a deposit to proceed even when `totalAssetDeposits` is exactly at the configured cap. This is the direct analog of the Aave exposure-ceiling bypass: a supply-cap control exists but is not consistently enforced across all deposit paths.

---

### Finding Description

In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
``` [1](#0-0) 

For ERC20 assets the prospective deposit `amount` is added to `totalAssetDeposits` before comparing against the cap, so any deposit that would push the total over the limit is correctly rejected. For ETH the `amount` parameter is never used: the function only checks whether the total is **already** strictly greater than the limit. When `totalAssetDeposits == depositLimitByAsset(ETH_TOKEN)` the check returns `false` (not exceeded), `_beforeDeposit` does not revert, and `depositETH` mints rsETH and accepts the ETH, pushing the running total above the configured cap. [2](#0-1) 

The deposit limit is set per-asset in `LRTConfig.depositLimitByAsset` and is the protocol's primary supply-cap control for ETH. [3](#0-2) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The ETH deposit cap is a protocol-level supply control. When `totalAssetDeposits` is exactly at the limit, any depositor can call `depositETH` with an arbitrary `msg.value` and receive freshly minted rsETH, pushing the total above the cap. This:

- Violates the invariant that `getTotalAssetDeposits(ETH_TOKEN) ≤ depositLimitByAsset(ETH_TOKEN)` after every deposit.
- Causes slightly more rsETH to be minted than the cap intends, diluting existing holders by a small amount.
- Does not directly steal funds; the depositor provides real ETH.

---

### Likelihood Explanation

**Low-Medium.** The condition `totalAssetDeposits == depositLimitByAsset(ETH_TOKEN)` must hold at the moment of the call. Because `getTotalAssetDeposits` aggregates across the deposit pool, NDCs, EigenLayer strategies, the converter, and the unstaking vault, the exact equality is transient but reachable — especially when an operator sets the limit to match the current total (a common operational pattern when capping further inflows). Any unprivileged depositor can trigger it with a single `depositETH` call. [4](#0-3) 

---

### Recommendation

Apply the same prospective check to ETH that is already applied to ERC20 tokens:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This makes the ETH and ERC20 paths consistent and ensures the cap is never exceeded regardless of the current total.

---

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 100 ether`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `100 ether`.
3. Alice calls `depositETH(0, "ref")` with `msg.value = 1 ether`.
4. `_beforeDeposit(ETH_TOKEN, 1 ether, 0)` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 1 ether)`.
5. Inside the function: `totalAssetDeposits = 100 ether`, `depositLimit = 100 ether`.
6. ETH branch: `100 ether > 100 ether` → `false` → limit not considered exceeded.
7. `_beforeDeposit` does not revert; `_mintRsETH` mints rsETH for Alice.
8. `getTotalAssetDeposits(ETH_TOKEN)` is now `101 ether`, exceeding the cap by `1 ether`. [5](#0-4) [1](#0-0)

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

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
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

**File:** contracts/LRTConfig.sol (L23-23)
```text
    mapping(address token => uint256 amount) public depositLimitByAsset;
```
