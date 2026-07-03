### Title
Newly Added Supported Asset Without `assetPriceOracle` Entry Permanently Blocks `LRTOracle.updateRSETHPrice` — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTConfig.addNewSupportedAsset()` does not enforce that a corresponding price oracle entry exists in `LRTOracle` before appending the asset to `supportedAssetList`. When `updateRSETHPrice()` is subsequently called, `_getTotalEthInProtocol()` iterates over every entry in `supportedAssetList` and calls `getAssetPrice(asset)` for each. If any asset lacks an `assetPriceOracle` entry, the `onlySupportedOracle` modifier reverts with `AssetOracleNotSupported`, permanently blocking the rsETH price update mechanism until admin remediation.

---

### Finding Description

`LRTConfig.addNewSupportedAsset()` is callable by the `TIME_LOCK_ROLE` and adds an asset to `supportedAssetList` with no check that `LRTOracle.assetPriceOracle[asset]` is populated: [1](#0-0) 

`LRTOracle._getTotalEthInProtocol()` fetches the full `supportedAssetList` from `LRTConfig` and calls `getAssetPrice(asset)` for every element in the list: [2](#0-1) 

`getAssetPrice` is guarded by the `onlySupportedOracle` modifier, which reverts unconditionally when `assetPriceOracle[asset] == address(0)`: [3](#0-2) [4](#0-3) 

`_getTotalEthInProtocol()` is called inside `_updateRsETHPrice()`, which is invoked by the public `updateRSETHPrice()`: [5](#0-4) [6](#0-5) 

The `updatePriceOracleFor` function in `LRTOracle` does not require the asset to be supported before setting its oracle — meaning the oracle can be set before or after `addNewSupportedAsset`, but there is no enforcement of ordering: [7](#0-6) 

---

### Impact Explanation

Once a new asset is added to `LRTConfig` without a corresponding `assetPriceOracle` entry, every call to `updateRSETHPrice()` (public) and `updateRSETHPriceAsManager()` (manager-only) reverts. The stored `rsETHPrice` becomes permanently stale until admin remediation (either setting the oracle or removing the asset). A stale `rsETHPrice` means:

- Protocol yield accrual and fee minting via `_updateRsETHPrice` are frozen.
- All subsequent deposits and withdrawals use the stale price, causing incorrect rsETH minting and incorrect asset payouts.

**Impact: Medium — Temporary freezing of unclaimed yield / temporary freezing of funds** (recoverable only by privileged admin action).

---

### Likelihood Explanation

The `TIME_LOCK_ROLE` holder adding a new LST asset is a routine protocol expansion operation. The two required steps — `addNewSupportedAsset` in `LRTConfig` and `updatePriceOracleFor` in `LRTOracle` — are in separate contracts with no on-chain coupling. A deployment sequencing error or a missed step during a governance proposal is a realistic operational mistake. Likelihood: **Low-Medium**.

---

### Recommendation

In `LRTConfig.addNewSupportedAsset()` (or its internal `_addNewSupportedAsset`), enforce that `LRTOracle.assetPriceOracle[asset]` is already set before appending the asset to `supportedAssetList`. Alternatively, add the oracle entry atomically in the same transaction as the asset addition, or add a validation call to `LRTOracle.getAssetPrice(asset)` inside `_addNewSupportedAsset` to confirm the oracle is live before proceeding.

---

### Proof of Concept

1. `TIME_LOCK_ROLE` calls `LRTConfig.addNewSupportedAsset(newLST, depositLimit)`.
   - `newLST` is appended to `supportedAssetList`.
   - No oracle is set in `LRTOracle` for `newLST` (`assetPriceOracle[newLST] == address(0)`).

2. Any caller (including an unprivileged user) calls `LRTOracle.updateRSETHPrice()`.

3. Execution path:
   - `updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()`
   - Loop reaches `newLST`: calls `getAssetPrice(newLST)`
   - `onlySupportedOracle(newLST)` checks `assetPriceOracle[newLST] == address(0)` → **reverts with `AssetOracleNotSupported`**

4. `rsETHPrice` is never updated. Fee minting is frozen. All deposits and withdrawals use the stale price until admin sets the oracle or removes the asset. [8](#0-7)

### Citations

**File:** contracts/LRTConfig.sol (L99-118)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }

    /// @dev private function to add a new supported asset
    /// @param asset Asset address
    /// @param depositLimit Deposit limit for the asset
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

**File:** contracts/LRTOracle.sol (L40-45)
```text
    modifier onlySupportedOracle(address asset) {
        if (assetPriceOracle[asset] == address(0)) {
            revert AssetOracleNotSupported();
        }
        _;
    }
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

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
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
