### Title
`removeSupportedAsset()` Does Not Clear Stale `assetPriceOracle` Entry, Causing Incorrect rsETH Price on Asset Re-addition - (File: contracts/LRTConfig.sol)

---

### Summary

`removeSupportedAsset()` in `LRTConfig.sol` cleans up several storage slots for a removed asset but omits clearing `assetPriceOracle[asset]` in `LRTOracle.sol`. When the same asset is later re-added via `addNewSupportedAsset()`, the stale oracle entry is silently reactivated and used in rsETH price calculations without any explicit re-validation, mirroring the incomplete-cleanup pattern of the reference bug.

---

### Finding Description

`removeSupportedAsset()` deletes four pieces of state:

```solidity
// LRTConfig.sol L86-91
delete isSupportedAsset[asset];
delete assetStrategy[asset];
depositLimitByAsset[asset] = 0;
supportedAssetList[tokenIndex] = supportedAssetList[supportedAssetList.length - 1];
supportedAssetList.pop();
``` [1](#0-0) 

It does **not** call `LRTOracle.updatePriceOracleFor(asset, address(0))` to clear the fifth piece of associated state:

```solidity
// LRTOracle.sol L26
mapping(address asset => address priceOracle) public override assetPriceOracle;
``` [2](#0-1) 

`_addNewSupportedAsset()` — called by `addNewSupportedAsset()` — never sets or validates an oracle:

```solidity
// LRTConfig.sol L106-118
function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
    ...
    isSupportedAsset[asset] = true;
    supportedAssetList.push(asset);
    depositLimitByAsset[asset] = depositLimit;
    emit AddedNewSupportedAsset(asset, depositLimit);
}
``` [3](#0-2) 

So on re-addition the stale `assetPriceOracle[asset]` is immediately live again. `_getTotalEthInProtocol()` iterates `supportedAssetList` and calls `getAssetPrice(asset)` for every entry:

```solidity
// LRTOracle.sol L336-343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // uses assetPriceOracle[asset]
    uint256 totalAssetAmt = ILRTDepositPool(...).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
``` [4](#0-3) 

`getAssetPrice` delegates directly to the stored oracle address with no freshness check:

```solidity
// LRTOracle.sol L156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [5](#0-4) 

`updatePriceOracleFor` does allow clearing the oracle to `address(0)` while the asset is unsupported, but `removeSupportedAsset()` never invokes it:

```solidity
// LRTOracle.sol L113-119
function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
    if (lrtConfig.isSupportedAsset(asset)) {
        UtilLib.checkNonZeroAddress(priceOracle);   // only enforced while supported
    }
    assetPriceOracle[asset] = priceOracle;
    ...
}
``` [6](#0-5) 

---

### Impact Explanation

If the stale oracle contract is deprecated, returns a wrong price, or reverts, the consequences are:

- **Wrong price path:** `_updateRsETHPrice()` computes an incorrect `totalETHInProtocol`, producing a wrong `rsETHPrice`. Every subsequent `getRsETHAmountToMint()` call uses this price, so depositors receive too many or too few rsETH tokens — a share/asset mis-accounting issue.
- **Reverting oracle path:** `_getTotalEthInProtocol()` reverts, blocking `updateRSETHPrice()` entirely and freezing the rsETH exchange rate.

**Severity: Low** — contract fails to deliver promised returns (incorrect rsETH minting ratio) without direct fund loss, or at worst a temporary freeze of the price-update path.

---

### Likelihood Explanation

The scenario requires two sequential admin actions: remove an asset, then re-add it (e.g., after a temporary suspension or strategy migration). Neither action is exotic — both are documented admin operations. The oversight of not re-setting the oracle before re-adding is a realistic operational mistake, especially since `addNewSupportedAsset()` gives no indication that an oracle must be separately refreshed.

---

### Recommendation

Inside `removeSupportedAsset()` in `LRTConfig.sol`, after removing the asset from `supportedAssetList`, call the oracle contract to clear the stale entry:

```solidity
address lrtOracleAddress = getContract(LRTConstants.LRT_ORACLE);
ILRTOracle(lrtOracleAddress).updatePriceOracleFor(asset, address(0));
```

This mirrors the fix recommended for the reference bug: explicitly clean up every piece of associated state at removal time so that re-registration starts from a clean slate.

---

### Proof of Concept

1. Asset `X` is supported; `LRTOracle.assetPriceOracle[X]` points to oracle `O1`.
2. Admin calls `LRTConfig.removeSupportedAsset(X, idx)`.
   - `isSupportedAsset[X]` → deleted; `assetStrategy[X]` → deleted; `depositLimitByAsset[X]` → 0; `supportedAssetList` updated.
   - `LRTOracle.assetPriceOracle[X]` **remains `O1`** — not touched.
3. Oracle `O1` is deprecated (returns stale/wrong price or reverts).
4. Admin calls `LRTConfig.addNewSupportedAsset(X, newLimit)` to re-list the asset.
   - `isSupportedAsset[X]` → true; `supportedAssetList` includes `X` again.
   - `LRTOracle.assetPriceOracle[X]` **still `O1`** — no oracle update was required or prompted.
5. Anyone calls `LRTOracle.updateRSETHPrice()`.
   - `_getTotalEthInProtocol()` iterates `supportedAssetList`, hits asset `X`, calls `getAssetPrice(X)` → delegates to stale `O1`.
   - If `O1` returns a wrong value: `rsETHPrice` is miscalculated; all subsequent deposits mint incorrect rsETH amounts via `getRsETHAmountToMint()`.
   - If `O1` reverts: `updateRSETHPrice()` reverts, freezing the rsETH price. [7](#0-6) [8](#0-7)

### Citations

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

**File:** contracts/LRTConfig.sol (L106-118)
```text
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```

**File:** contracts/LRTOracle.sol (L26-26)
```text
    mapping(address asset => address priceOracle) public override assetPriceOracle;
```

**File:** contracts/LRTOracle.sol (L113-119)
```text
    function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
        if (lrtConfig.isSupportedAsset(asset)) {
            UtilLib.checkNonZeroAddress(priceOracle);
        }
        assetPriceOracle[asset] = priceOracle;
        emit AssetPriceOracleUpdate(asset, priceOracle);
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
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
