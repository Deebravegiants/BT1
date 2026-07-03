### Title
`updateRSETHPrice()` DoS via Missing Oracle for Newly Added Supported Asset — (`contracts/LRTOracle.sol`)

### Summary
`LRTOracle._getTotalEthInProtocol()` iterates over every address in `supportedAssetList` and calls `getAssetPrice(asset)` for each one. If any asset in that list has no oracle configured (`assetPriceOracle[asset] == address(0)`), the call reverts unconditionally. Because `addNewSupportedAsset()` in `LRTConfig` adds an asset to `supportedAssetList` without atomically requiring a corresponding oracle entry in `LRTOracle`, a window exists where `updateRSETHPrice()` is permanently broken until the oracle is separately configured.

### Finding Description
`LRTOracle._getTotalEthInProtocol()` is the private function that computes total protocol TVL and is the sole input to `_updateRsETHPrice()`:

```solidity
// contracts/LRTOracle.sol  lines 331-349
function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
    address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
    address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
    uint256 supportedAssetCount = supportedAssets.length;

    for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
        address asset = supportedAssets[assetIdx];
        uint256 assetER = getAssetPrice(asset);   // ← reverts if oracle == address(0)
        ...
    }
}
```

`getAssetPrice` is guarded by:

```solidity
// contracts/LRTOracle.sol  lines 40-44
modifier onlySupportedOracle(address asset) {
    if (assetPriceOracle[asset] == address(0)) {
        revert AssetOracleNotSupported();
    }
    _;
}
```

`addNewSupportedAsset()` in `LRTConfig` pushes the asset into `supportedAssetList` with no requirement that `LRTOracle.assetPriceOracle[asset]` is already set:

```solidity
// contracts/LRTConfig.sol  lines 99-101
function addNewSupportedAsset(address asset, uint256 depositLimit)
    external onlyRole(LRTConstants.TIME_LOCK_ROLE)
{
    _addNewSupportedAsset(asset, depositLimit);
}
```

`updatePriceOracleFor()` in `LRTOracle` is a separate call, gated by a different role (`onlyLRTAdmin`), and is not enforced atomically with asset addition:

```solidity
// contracts/LRTOracle.sol  lines 113-119
function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
    if (lrtConfig.isSupportedAsset(asset)) {
        UtilLib.checkNonZeroAddress(priceOracle);
    }
    assetPriceOracle[asset] = priceOracle;
    ...
}
```

**Scenario:**
1. `TIME_LOCK_ROLE` calls `addNewSupportedAsset(newAsset, limit)` — `newAsset` is now in `supportedAssetList`.
2. `LRTAdmin` has not yet called `updatePriceOracleFor(newAsset, oracle)` — `assetPriceOracle[newAsset] == address(0)`.
3. Anyone calls `updateRSETHPrice()`.
4. `_getTotalEthInProtocol()` reaches `newAsset`, calls `getAssetPrice(newAsset)`, hits `onlySupportedOracle`, and reverts with `AssetOracleNotSupported`.
5. `updateRSETHPrice()` is completely blocked until the oracle is configured.

### Impact Explanation
`updateRSETHPrice()` is the public entry point that keeps the stored `rsETHPrice` current. While deposits and withdrawals read the cached `rsETHPrice` rather than calling `_updateRsETHPrice()` inline, a stale price directly affects the rsETH-to-asset exchange rate used in `getRsETHAmountToMint()` (deposits) and `getExpectedAssetAmount()` (withdrawals). If the true protocol TVL has grown since the last successful price update, depositors receive more rsETH than warranted, diluting existing holders' yield. The contract fails to deliver its promised accurate exchange rate for the duration of the DoS window.

**Impact level:** Low — contract fails to deliver promised returns; no direct loss of principal.

### Likelihood Explanation
`addNewSupportedAsset` and `updatePriceOracleFor` are controlled by different roles (`TIME_LOCK_ROLE` vs `LRTAdmin`) and are separate transactions. Any multi-step asset onboarding process creates a window — however brief — where the oracle entry is absent. The window is bounded by the time between the two admin transactions, but during that window every call to `updateRSETHPrice()` reverts.

### Recommendation
Enforce atomicity between asset registration and oracle configuration. One approach: require that `assetPriceOracle[asset]` is already set in `LRTOracle` before `addNewSupportedAsset` completes, or add a check inside `_getTotalEthInProtocol()` to skip assets whose oracle is not yet configured (analogous to the recommended fix in the external report — skip rather than revert):

```solidity
// contracts/LRTOracle.sol
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    if (assetPriceOracle[asset] == address(0)) {
        unchecked { ++assetIdx; }
        continue;  // skip assets with no oracle instead of reverting
    }
    uint256 assetER = getAssetPrice(asset);
    ...
}
```

### Proof of Concept
1. Deploy protocol with assets `[stETH, ETHx]`, both with oracles set.
2. `TIME_LOCK_ROLE` calls `LRTConfig.addNewSupportedAsset(newLST, limit)`.
3. `LRTAdmin` has not yet called `LRTOracle.updatePriceOracleFor(newLST, oracle)`.
4. Call `LRTOracle.updateRSETHPrice()` — transaction reverts with `AssetOracleNotSupported`.
5. `rsETHPrice` is now frozen at its last value; all subsequent deposit/withdrawal exchange rates are computed against a stale price until step 3 is executed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L40-44)
```text
    modifier onlySupportedOracle(address asset) {
        if (assetPriceOracle[asset] == address(0)) {
            revert AssetOracleNotSupported();
        }
        _;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```
