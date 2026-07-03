Based on my analysis of the code, this is a valid Medium vulnerability. Here is the full finding:

---

### Title
`updateRSETHPrice()` Permanently Reverts When a Supported Asset Has No Oracle Configured — (`contracts/LRTOracle.sol`)

### Summary
`_getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every asset in `lrtConfig.getSupportedAssetList()`. `getAssetPrice` guards with `onlySupportedOracle`, which reverts with `AssetOracleNotSupported()` if `assetPriceOracle[asset] == address(0)`. Two legitimate admin flows can produce this state, causing `updateRSETHPrice()` and `updateRSETHPriceAsManager()` to always revert and freezing `rsETHPrice` at its last stored value.

### Finding Description

**Root cause — `updatePriceOracleFor` allows `address(0)` for unsupported assets:** [1](#0-0) 

The zero-address guard fires only when the asset is already supported. An admin can call `updatePriceOracleFor(asset, address(0))` while `asset` is not yet in `lrtConfig.supportedAssetList`, storing `address(0)` in `assetPriceOracle`. When `addNewSupportedAsset` later adds that asset, the oracle mapping is never updated.

**Root cause — `addNewSupportedAsset` has no oracle requirement:** [2](#0-1) 

`_addNewSupportedAsset` sets `isSupportedAsset[asset] = true` and pushes to `supportedAssetList` with no check that `LRTOracle.assetPriceOracle[asset]` is non-zero. There is no atomic "add asset + set oracle" operation, so there is always a window (or a permanent state if the oracle is never set) where the asset is supported but has no oracle.

**Revert propagation chain:**

`getAssetPrice` modifier: [3](#0-2) 

`_getTotalEthInProtocol` calls `getAssetPrice` for every supported asset: [4](#0-3) 

`_updateRsETHPrice` calls `_getTotalEthInProtocol`: [5](#0-4) 

Both public entry points call `_updateRsETHPrice`: [6](#0-5) 

### Impact Explanation

`rsETHPrice` is frozen at its last stored value. Downstream consumers that read the stale stored value (`LRTDepositPool.getRsETHAmountToMint` via `lrtOracle.rsETHPrice()`, `LRTWithdrawalManager.getExpectedAssetAmount`) continue to operate but at an incorrect, stale price. No new price update can succeed until an admin sets a valid oracle for the offending asset. This matches **Medium — Temporary freezing of funds** (price oracle frozen, incorrect mint/burn ratios for all users during the outage). [7](#0-6) 

### Likelihood Explanation

Requires a privileged admin action, but the action itself is legitimate and the protocol provides no safeguard against it. The two realistic triggers are:

1. Admin pre-registers an oracle mapping as `address(0)` for a future asset (explicitly permitted by `updatePriceOracleFor`), then the asset is added via `addNewSupportedAsset`.
2. Admin adds a new supported asset and delays setting its oracle (no atomic combined operation exists).

Neither requires malicious intent; both are normal operational sequences.

### Recommendation

1. In `updatePriceOracleFor`, always reject `priceOracle == address(0)` regardless of whether the asset is currently supported:
   ```solidity
   function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
       UtilLib.checkNonZeroAddress(priceOracle); // unconditional
       assetPriceOracle[asset] = priceOracle;
       emit AssetPriceOracleUpdate(asset, priceOracle);
   }
   ```
2. In `_addNewSupportedAsset` (or `addNewSupportedAsset`), require that `LRTOracle.assetPriceOracle[asset] != address(0)` before marking the asset as supported, or provide an atomic `addAssetWithOracle` function.
3. Add a pre-flight check in `_getTotalEthInProtocol` that skips (or reverts with a clear error) assets whose oracle is `address(0)`, to prevent a single misconfigured asset from bricking the entire price-update path.

### Proof of Concept

```solidity
// Local fork / unit test — no mainnet interaction
function test_frozenPrice_missingOracle() public {
    // 1. Admin pre-registers oracle as address(0) for a future asset
    vm.prank(admin);
    lrtOracle.updatePriceOracleFor(newAsset, address(0));
    // assetPriceOracle[newAsset] == address(0) — allowed by current code

    // 2. TIME_LOCK_ROLE adds the asset to the supported list
    vm.prank(timeLockRole);
    lrtConfig.addNewSupportedAsset(newAsset, 100_000 ether);
    // newAsset is now in getSupportedAssetList() but oracle is still address(0)

    // 3. updateRSETHPrice() reverts
    vm.expectRevert(ILRTOracle.AssetOracleNotSupported.selector);
    lrtOracle.updateRSETHPrice();

    // 4. updateRSETHPriceAsManager() also reverts
    vm.prank(manager);
    vm.expectRevert(ILRTOracle.AssetOracleNotSupported.selector);
    lrtOracle.updateRSETHPriceAsManager();

    // rsETHPrice is now permanently stale until admin fixes the oracle
}
```

### Citations

**File:** contracts/LRTOracle.sol (L40-45)
```text
    modifier onlySupportedOracle(address asset) {
        if (assetPriceOracle[asset] == address(0)) {
            revert AssetOracleNotSupported();
        }
        _;
    }
```

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
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

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
