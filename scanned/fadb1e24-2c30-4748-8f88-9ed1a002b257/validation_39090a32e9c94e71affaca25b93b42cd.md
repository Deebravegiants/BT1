### Title
Missing Zero-Address Guard on `assetPriceFeed` Causes `updateRSETHPrice()` to Revert — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` performs no check that `assetPriceFeed[asset]` is non-zero before calling `latestRoundData()` on it. If a new asset is added to `LRTConfig` and its oracle is registered in `LRTOracle` (via the unvalidated `updatePriceOracleFor`) before `ChainlinkPriceOracle.updatePriceFeedFor` is called, the mapping entry remains `address(0)`. Any subsequent call to `updateRSETHPrice()` will revert, temporarily freezing the price update mechanism.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice` casts `assetPriceFeed[asset]` directly to `AggregatorV3Interface` and calls `latestRoundData()` on it: [1](#0-0) 

The `onlySupportedAsset` modifier only verifies that the asset is registered in `LRTConfig.isSupportedAsset`; it does **not** verify that `assetPriceFeed[asset]` is non-zero: [2](#0-1) 

When `assetPriceFeed[asset] == address(0)`, the EVM executes a `CALL` to `address(0)`. Because `address(0)` has no code, the call returns success with **empty return data**. Solidity 0.8.27 then attempts to ABI-decode five return values (`uint80, int256, uint256, uint256, uint80`) from zero bytes, which causes an unconditional revert.

This revert propagates through the full call chain:

`updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `LRTOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice(asset)` → **revert** [3](#0-2) 

The `onlySupportedOracle` modifier in `LRTOracle` only checks that `assetPriceOracle[asset] != address(0)` (i.e., that a price oracle contract is registered), not that the oracle's internal feed mapping is populated: [4](#0-3) 

The unvalidated `updatePriceOracleFor` path in `LRTOracle` allows registering `ChainlinkPriceOracle` for an asset without verifying that the feed is configured: [5](#0-4) 

(The validated variant `updatePriceOracleForValidated` would catch this because it calls `getAssetPrice` first, but it is not enforced.)

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

While `assetPriceFeed[asset]` remains `address(0)` for any asset in the supported list, every call to `updateRSETHPrice()` (and `updateRSETHPriceAsManager()`) reverts. The `rsETHPrice` state variable becomes stale. Any protocol flow that depends on a fresh price update (deposits that gate on price freshness, withdrawal processing, rsETH minting) is effectively frozen until an operator calls `ChainlinkPriceOracle.updatePriceFeedFor` with a valid feed address.

---

### Likelihood Explanation

The window opens whenever:
1. `LRTConfig.addNewSupportedAsset` is called (requires `TIME_LOCK_ROLE`), and
2. `LRTOracle.updatePriceOracleFor` is called to register `ChainlinkPriceOracle` for that asset (requires `LRTAdmin`), but
3. `ChainlinkPriceOracle.updatePriceFeedFor` has not yet been called for that asset.

This is a realistic operational sequence — adding a new asset involves multiple transactions across multiple roles, and there is no atomic or enforced ordering that prevents the oracle from being registered before the feed is set. The freeze persists until the feed is configured.

---

### Recommendation

Add an explicit zero-address guard in `ChainlinkPriceOracle.getAssetPrice`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    address feed = assetPriceFeed[asset];
    if (feed == address(0)) revert PriceFeedNotConfigured(asset);
    AggregatorV3Interface priceFeed = AggregatorV3Interface(feed);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, enforce that `updatePriceOracleForValidated` (which calls `getAssetPrice` as a sanity check) is the only permitted path for registering a new oracle, or add a corresponding check in `updatePriceOracleFor`.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Assume a local/fork test environment with LRTConfig, LRTOracle, ChainlinkPriceOracle deployed.

function testTemporaryFreeze() public {
    address newAsset = address(0xBEEF); // mock ERC-20

    // Step 1: Admin adds new asset to LRTConfig (no price feed configured yet)
    vm.prank(timeLockAdmin);
    lrtConfig.addNewSupportedAsset(newAsset, 100_000 ether);

    // Step 2: Admin registers ChainlinkPriceOracle for the new asset in LRTOracle
    // Uses unvalidated path — no feed check performed
    vm.prank(lrtAdmin);
    lrtOracle.updatePriceOracleFor(newAsset, address(chainlinkPriceOracle));

    // Step 3: assetPriceFeed[newAsset] is still address(0) in ChainlinkPriceOracle

    // Step 4: Any caller triggers updateRSETHPrice — it reverts
    vm.expectRevert();
    lrtOracle.updateRSETHPrice();

    // Step 5: Confirm ChainlinkPriceOracle.getAssetPrice also reverts
    vm.expectRevert();
    chainlinkPriceOracle.getAssetPrice(newAsset);
}
``` [1](#0-0) [6](#0-5) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L65-70)
```text
    modifier onlySupportedAsset(address asset) {
        if (!lrtConfig.isSupportedAsset(asset)) {
            revert ILRTConfig.AssetNotSupported();
        }
        _;
    }
```

**File:** contracts/LRTOracle.sol (L40-45)
```text
    modifier onlySupportedOracle(address asset) {
        if (assetPriceOracle[asset] == address(0)) {
            revert AssetOracleNotSupported();
        }
        _;
    }
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

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```
