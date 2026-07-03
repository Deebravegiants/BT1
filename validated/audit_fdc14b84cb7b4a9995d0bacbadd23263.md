### Title
Asset Can Be Added as Supported Without a Price Oracle, Freezing Deposits and Breaking Protocol-Wide Price Updates - (File: contracts/LRTConfig.sol)

### Summary

`LRTConfig._addNewSupportedAsset` registers an asset as supported without verifying that a corresponding price oracle has been configured in `LRTOracle`. Once the asset is listed, any call to `LRTDepositPool.depositAsset` for that asset reverts, and — more critically — `LRTOracle.updateRSETHPrice` reverts for **every** asset in the protocol, freezing fee minting and price tracking until the oracle is manually added.

### Finding Description

`LRTConfig._addNewSupportedAsset` (called by the `TIME_LOCK_ROLE`-gated `addNewSupportedAsset`) marks an asset as supported and sets its deposit limit, but performs no check that `LRTOracle.assetPriceOracle[asset]` is non-zero: [1](#0-0) 

The oracle for an asset is set separately via `LRTOracle.updatePriceOracleFor` (or `updatePriceOracleForValidated`), which is a distinct admin transaction: [2](#0-1) 

If the oracle-registration step is omitted or delayed, two failure paths open up:

**Path 1 — Deposit reverts for the new asset.**
`LRTDepositPool.depositAsset` calls `getRsETHAmountToMint`, which calls `lrtOracle.getAssetPrice(asset)`. `getAssetPrice` is guarded by `onlySupportedOracle`, which reverts with `AssetOracleNotSupported` when `assetPriceOracle[asset] == address(0)`: [3](#0-2) [4](#0-3) [5](#0-4) 

**Path 2 — `updateRSETHPrice()` reverts for the entire protocol.**
`_updateRsETHPrice` calls `_getTotalEthInProtocol`, which iterates **all** entries in `lrtConfig.getSupportedAssetList()` and calls `getAssetPrice` for each: [6](#0-5) 

A single oracle-less asset in the supported list causes this loop to revert, making `updateRSETHPrice()` (public) and `updateRSETHPriceAsManager()` both uncallable. This breaks fee minting, TVL accounting, and the price-deviation circuit-breaker for the entire protocol until the oracle is registered.

### Impact Explanation

**Medium — Temporary freezing of unclaimed yield and protocol-wide price updates.**

- Deposits for the oracle-less asset are completely blocked.
- `updateRSETHPrice()` reverts for all assets, halting fee minting (`_checkAndUpdateDailyFeeMintLimit` is never reached) and preventing the price-deviation circuit-breaker from functioning.
- No funds are permanently lost, but yield accrual and price tracking are frozen for the duration of the misconfiguration window.

### Likelihood Explanation

**Medium.** Adding a new supported asset and registering its oracle are two separate privileged transactions with no on-chain coupling. A deployment script error, a governance proposal that only executes the first step, or a simple operational oversight can leave the protocol in the broken state. The `TIME_LOCK_ROLE` gating on `addNewSupportedAsset` means the window between the two steps can span the timelock delay (hours to days), during which the protocol is degraded.

### Recommendation

Inside `_addNewSupportedAsset`, require that a valid price oracle is already registered in `LRTOracle` for the asset before marking it as supported:

```solidity
function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
    UtilLib.checkNonZeroAddress(asset);
    if (depositLimit == 0) revert InvalidDepositLimit();
    if (isSupportedAsset[asset]) revert AssetAlreadySupported();

    // Ensure a price oracle is already configured
    address lrtOracle = contractMap[LRTConstants.LRT_ORACLE];
    if (lrtOracle != address(0)) {
        require(
            ILRTOracle(lrtOracle).assetPriceOracle(asset) != address(0),
            "Oracle not set for asset"
        );
    }

    isSupportedAsset[asset] = true;
    supportedAssetList.push(asset);
    depositLimitByAsset[asset] = depositLimit;
    emit AddedNewSupportedAsset(asset, depositLimit);
}
```

Alternatively, combine the oracle registration and asset listing into a single atomic admin function so the two steps cannot be separated.

### Proof of Concept

1. Admin calls `LRTConfig.addNewSupportedAsset(newAsset, depositLimit)` — succeeds; `isSupportedAsset[newAsset] = true`.
2. Admin does **not** call `LRTOracle.updatePriceOracleFor(newAsset, oracle)` (omitted or delayed by timelock).
3. Any user calls `LRTDepositPool.depositAsset(newAsset, amount, 0, "")`:
   - Passes `onlySupportedERC20Token(newAsset)` ✓
   - Calls `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(newAsset)`
   - `onlySupportedOracle` fires: `assetPriceOracle[newAsset] == address(0)` → **reverts with `AssetOracleNotSupported`**
4. Any caller (including keeper bots) calls `LRTOracle.updateRSETHPrice()`:
   - Calls `_getTotalEthInProtocol()` → loops over `supportedAssetList`
   - Hits `getAssetPrice(newAsset)` → **reverts with `AssetOracleNotSupported`**
   - Fee minting, TVL accounting, and price-deviation protection are all frozen until step 2 is executed.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
