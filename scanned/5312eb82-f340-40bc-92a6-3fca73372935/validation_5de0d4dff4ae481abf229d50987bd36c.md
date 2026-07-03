Looking at the exact code path in `LRTOracle.sol` and `LRTConfig.sol`:

The code path is fully traceable and the vulnerability is real. Here is the complete analysis:

**Call chain:**
- `updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` (for every asset in `supportedAssetList`) → `onlySupportedOracle` modifier → **reverts** if `assetPriceOracle[asset] == address(0)`

**The design gap:**
- `LRTConfig.addNewSupportedAsset` (requires `TIME_LOCK_ROLE`) pushes an asset into `supportedAssetList` with **no oracle set** in `LRTOracle`.
- `LRTOracle.updatePriceOracleFor` (requires `onlyLRTAdmin`) is a **separate, independent transaction** that sets the oracle.
- There is no atomicity requirement or enforcement that the oracle must be set before or simultaneously with asset addition.
- `updatePriceOracleFor` does guard against zeroing an oracle for an already-supported asset (line 114–115), but this does nothing to prevent the window between asset addition and oracle assignment.

**Realistic trigger:** Since `addNewSupportedAsset` requires `TIME_LOCK_ROLE` (implying a timelock delay), and `updatePriceOracleFor` requires `onlyLRTAdmin`, there is a natural operational window — potentially hours or days — during which the asset is in `supportedAssetList` but `assetPriceOracle[asset] == address(0)`. During this window every call to `updateRSETHPrice()` reverts.

This is not an admin compromise scenario; it is a code-level design gap where two separate privileged operations must be sequenced correctly but the contract does not enforce that ordering.

---

### Title
Missing oracle assignment enforcement on asset addition causes `updateRSETHPrice` to revert, leaving `rsETHPrice` permanently stale — (`contracts/LRTOracle.sol`)

### Summary
`LRTConfig.addNewSupportedAsset` adds an asset to `supportedAssetList` without requiring a corresponding price oracle to be registered in `LRTOracle`. Because `_getTotalEthInProtocol` calls `getAssetPrice` for every supported asset, and `getAssetPrice` reverts via the `onlySupportedOracle` modifier when `assetPriceOracle[asset] == address(0)`, any supported asset without an oracle causes `updateRSETHPrice` to revert entirely, leaving `rsETHPrice` stale.

### Finding Description
`LRTConfig._addNewSupportedAsset` registers an asset in `supportedAssetList` and sets its deposit limit, but performs no oracle check and makes no call to `LRTOracle`: [1](#0-0) 

The oracle is set by a separate, independent admin call to `LRTOracle.updatePriceOracleFor`, which requires `onlyLRTAdmin`: [2](#0-1) 

`updatePriceOracleFor` does prevent zeroing an oracle for an already-supported asset (line 114–115), but this guard only applies when *updating* an existing oracle — it does nothing to prevent the window between asset addition and initial oracle assignment.

`_getTotalEthInProtocol` iterates over every asset in `supportedAssetList` and calls `getAssetPrice` unconditionally: [3](#0-2) 

`getAssetPrice` applies the `onlySupportedOracle` modifier, which reverts with `AssetOracleNotSupported` when `assetPriceOracle[asset] == address(0)`: [4](#0-3) [5](#0-4) 

Because `_getTotalEthInProtocol` is called inside `_updateRsETHPrice`, which is called by both `updateRSETHPrice` and `updateRSETHPriceAsManager`, both entry points revert for the entire duration of the window. [6](#0-5) 

### Impact Explanation
While the oracle-less asset is in `supportedAssetList`, `rsETHPrice` cannot be updated. All deposits during this window use the last stale price to compute `rsethAmountToMint`, potentially minting rsETH at an incorrect rate. No funds are lost directly, but the contract fails to deliver its core promise of an up-to-date exchange rate. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation
`addNewSupportedAsset` requires `TIME_LOCK_ROLE`, which by design introduces a delay before execution. `updatePriceOracleFor` requires `onlyLRTAdmin` and is a separate transaction. The operational gap between these two steps is inherent to the timelock model and is therefore a realistic, non-negligible window in every new asset onboarding.

### Recommendation
Enforce oracle assignment atomically with asset addition. One approach: require the oracle address as a parameter in `addNewSupportedAsset` (or a wrapper) and call `updatePriceOracleFor` within the same transaction. Alternatively, add a pre-flight check in `_getTotalEthInProtocol` that skips (or reverts with a clear error on) assets whose oracle is `address(0)`, and separately add a validation in `addNewSupportedAsset` that the oracle is already registered before the asset is pushed to `supportedAssetList`.

### Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Foundry unit test (local, no mainnet fork required)
// 1. Deploy LRTConfig, LRTOracle, mock rsETH with nonzero totalSupply.
// 2. Grant TIME_LOCK_ROLE to address(this).
// 3. Call lrtConfig.addNewSupportedAsset(newAsset, 1 ether);
//    → newAsset is now in supportedAssetList
//    → lrtOracle.assetPriceOracle[newAsset] == address(0)
// 4. Call lrtOracle.updateRSETHPrice();
//    → _getTotalEthInProtocol() calls getAssetPrice(newAsset)
//    → onlySupportedOracle reverts with AssetOracleNotSupported
// 5. Assert the call reverted — rsETHPrice is now permanently stale
//    until an admin separately calls updatePriceOracleFor.

function test_updateRSETHPrice_revertsWhenAssetHasNoOracle() public {
    address newAsset = address(new MockERC20());
    lrtConfig.addNewSupportedAsset(newAsset, 1 ether); // TIME_LOCK_ROLE
    // oracle NOT set for newAsset in lrtOracle

    vm.expectRevert(ILRTOracle.AssetOracleNotSupported.selector);
    lrtOracle.updateRSETHPrice();
}
```

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

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
