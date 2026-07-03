### Title
Removed Supported Asset Excluded from TVL Accounting Causes rsETH Price Drop and Permanent Fund Freeze — (File: contracts/LRTConfig.sol)

---

### Summary

`LRTConfig.removeSupportedAsset()` removes an asset from `supportedAssetList` and simultaneously deletes `assetStrategy[asset]`. Because `LRTOracle._getTotalEthInProtocol()` and `LRTDepositPool._checkResidueLSTBalance()` both iterate exclusively over `supportedAssetList`, any residual deposits of the removed asset are silently excluded from TVL computation and from NodeDelegator residual-balance checks. This causes the rsETH exchange rate to drop and can permanently freeze the residual assets.

---

### Finding Description

**Root cause — `LRTConfig.removeSupportedAsset`** [1](#0-0) 

The function gates removal on:

```solidity
if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
    revert CannotRemoveAssetWithDeposits(asset);
}
``` [2](#0-1) 

`maxNegligibleAmount` is a state variable in `LRTConfig` settable at any time by `DEFAULT_ADMIN_ROLE` with no upper bound: [3](#0-2) [4](#0-3) 

After the guard passes, the function deletes both `isSupportedAsset[asset]` and `assetStrategy[asset]` and pops the asset from `supportedAssetList`: [5](#0-4) 

**Impact path 1 — rsETH price drop via `LRTOracle._getTotalEthInProtocol`**

The oracle computes the rsETH/ETH exchange rate by iterating only over `supportedAssetList`: [6](#0-5) 

Once an asset is removed from that list, its entire remaining balance (up to `maxNegligibleAmount` in value) is excluded from the TVL sum. The next call to `updateRSETHPrice()` / `_updateRsETHPrice()` computes a lower `totalETHInProtocol`, producing a lower `newRsETHPrice`, which is then stored as the canonical exchange rate: [7](#0-6) 

Every rsETH holder suffers an immediate, proportional loss of value.

**Impact path 2 — permanent fund freeze via `_checkResidueLSTBalance`**

When a NodeDelegator is removed from the queue, `_checkResidueLSTBalance` iterates only over `supportedAssetList`: [8](#0-7) 

Because the removed asset is no longer in `supportedAssetList`, any balance of that asset still held by the NodeDelegator — whether sitting in the NDC itself or staked in EigenLayer — is never checked. The NodeDelegator can be removed from the queue while those assets remain locked in EigenLayer with no recovery path, because `assetStrategy[asset]` was also deleted by `removeSupportedAsset`, making the strategy address `address(0)` for any future interaction.

---

### Impact Explanation

- **rsETH price drop**: All rsETH holders lose value proportional to the removed asset's share of TVL. The magnitude is bounded by `maxNegligibleAmount` but that parameter has no on-chain ceiling.
- **Permanent fund freeze**: Residual balances of the removed asset in EigenLayer become permanently inaccessible once the NodeDelegator is removed from the queue, because the strategy pointer is deleted and the asset is no longer recognized by any accounting function.

**Impact: Critical — Permanent freezing of funds / Protocol insolvency (rsETH price manipulation).**

---

### Likelihood Explanation

Requires the `DEFAULT_ADMIN_ROLE` to call `removeSupportedAsset` while residual deposits exist. The guard check is bypassable whenever `maxNegligibleAmount` is set to a value larger than the actual residual deposits — a configuration the same admin role can make at any time with no time-lock. This is a legitimate operational action (e.g., deprecating a low-liquidity LST) that carries unintended permanent consequences.

**Likelihood: Low.**

---

### Recommendation

1. **Enforce a hard zero-deposit requirement**: Replace the `maxNegligibleAmount` threshold with a strict `== 0` check for `getTotalAssetDeposits(asset)` before allowing removal, so no residual balance can ever be silently excluded.
2. **Do not delete `assetStrategy`**: Retain the strategy pointer so that any residual EigenLayer balance remains queryable and withdrawable even after the asset is de-listed.
3. **Extend `_checkResidueLSTBalance` to cover de-listed assets**: Maintain a separate "ever-supported" registry so that NodeDelegator removal checks all assets that were ever deposited, not only currently active ones.

---

### Proof of Concept

1. Protocol has asset `stETH` in `supportedAssetList` with 0.5 ether staked in EigenLayer via NodeDelegator NDC-1.
2. Admin calls `setMaxNegligibleAmount(1 ether)` — now any asset with ≤ 1 ether total deposits can be removed.
3. Admin calls `LRTConfig.removeSupportedAsset(stETH, idx)`. The guard check passes (`0.5 ether ≤ 1 ether`). `isSupportedAsset[stETH]`, `assetStrategy[stETH]`, and the `supportedAssetList` entry are all deleted.
4. Anyone calls `LRTOracle.updateRSETHPrice()`. `_getTotalEthInProtocol()` iterates `supportedAssetList` — stETH is absent. The 0.5 ether of stETH value is excluded from TVL. `newRsETHPrice` drops; all rsETH holders lose value.
5. Admin calls `LRTDepositPool.removeNodeDelegatorContractFromQueue(NDC-1)`. `_checkResidueLSTBalance` iterates `supportedAssetList` — stETH is absent, so NDC-1's 0.5 ether stETH in EigenLayer is never checked. The call succeeds. The 0.5 ether stETH is now permanently frozen in EigenLayer with no recovery path.

### Citations

**File:** contracts/LRTConfig.sol (L30-30)
```text
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTConfig.sol (L66-94)
```text
    function removeSupportedAsset(
        address asset,
        uint256 tokenIndex
    )
        external
        onlySupportedAsset(asset)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(asset);

        if (supportedAssetList[tokenIndex] != asset) {
            revert TokenNotFoundError();
        }

        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }

        delete isSupportedAsset[asset];
        delete assetStrategy[asset];
        depositLimitByAsset[asset] = 0;

        supportedAssetList[tokenIndex] = supportedAssetList[supportedAssetList.length - 1];
        supportedAssetList.pop();

        emit RemovedSupportedAsset(asset);
    }
```

**File:** contracts/LRTConfig.sol (L256-259)
```text
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyRole(DEFAULT_ADMIN_ROLE) {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L627-646)
```text
    function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetsLength = supportedAssets.length;

        uint256 assetBalance;
        for (uint256 i; i < supportedAssetsLength; ++i) {
            if (supportedAssets[i] == LRTConstants.ETH_TOKEN) {
                // this function only checks for residual LST balance
                continue;
            }

            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
        }
    }
```
