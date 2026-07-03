The code path is concrete. Let me verify the exact lines before writing the finding.

### Title
Missing oracle registration enforcement when adding a supported asset causes `updateRSETHPrice` to revert, leaving `rsETHPrice` permanently stale until remediated — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTConfig.addNewSupportedAsset` and `LRTOracle.updatePriceOracleFor` are independent, non-atomic operations. Adding a new supported asset without a corresponding oracle entry in `LRTOracle` causes every subsequent call to `updateRSETHPrice` to revert, freezing the rsETH exchange rate and causing all deposits to mint at a stale price.

---

### Finding Description

`LRTConfig.addNewSupportedAsset` appends an asset to `supportedAssetList` with no requirement that a price oracle has been registered in `LRTOracle`: [1](#0-0) 

`LRTOracle._getTotalEthInProtocol` iterates over every entry in that list and calls `getAssetPrice` for each: [2](#0-1) 

`getAssetPrice` is guarded by `onlySupportedOracle`, which reverts unconditionally when `assetPriceOracle[asset] == address(0)`: [3](#0-2) 

`updatePriceOracleFor` does enforce a non-zero oracle address — but **only when the asset is already supported**. This means the oracle can be pre-registered before the asset is added, but there is no enforcement of that ordering: [4](#0-3) 

The result: if `addNewSupportedAsset` executes before `updatePriceOracleFor` for the same asset (even transiently, across separate transactions), `_getTotalEthInProtocol` → `getAssetPrice` → `onlySupportedOracle` reverts, propagating up through `_updateRsETHPrice` and causing both `updateRSETHPrice` and `updateRSETHPriceAsManager` to revert entirely. [5](#0-4) 

---

### Impact Explanation

While `rsETHPrice` is stale, `getRsETHAmountToMint` uses the frozen price to compute how much rsETH to mint per deposited asset. Depositors receive an incorrect amount of rsETH — either over- or under-compensated relative to the true TVL — until the oracle is registered and `updateRSETHPrice` succeeds again. No funds are lost outright, but the contract fails to deliver the correct exchange rate it promises. This matches **Low: Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

`addNewSupportedAsset` requires `TIME_LOCK_ROLE` and is a timelocked operation. The oracle registration (`updatePriceOracleFor`) is a separate admin call in a different contract. There is no on-chain coupling between the two. A sequencing mistake — adding the asset before the oracle is set — is a realistic operational error, particularly during protocol upgrades or new LST onboarding. The window of breakage persists until the admin calls `updatePriceOracleFor` for the new asset.

---

### Recommendation

Enforce oracle registration atomically with asset addition. One approach: in `addNewSupportedAsset` (or its internal `_addNewSupportedAsset`), require that `LRTOracle.assetPriceOracle[asset] != address(0)` before the asset is appended to `supportedAssetList`. Alternatively, expose a combined admin function that calls both `addNewSupportedAsset` and `updatePriceOracleFor` atomically, or add a pre-flight check in `_getTotalEthInProtocol` that skips assets with no registered oracle (with an emitted warning) rather than reverting.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Pseudocode for a local Foundry test on unmodified contracts:

// 1. Deploy LRTConfig, LRTOracle, LRTDepositPool with standard setup.
// 2. Mint some rsETH so rsethSupply > 0 (so the early-return branch is skipped).
// 3. Call lrtConfig.addNewSupportedAsset(newAsset, depositLimit)
//    — newAsset has NO oracle set in LRTOracle (assetPriceOracle[newAsset] == address(0)).
// 4. Call lrtOracle.updateRSETHPrice().
// 5. Assert: call reverts with AssetOracleNotSupported().
// 6. Call lrtOracle.updatePriceOracleFor(newAsset, validOracle).
// 7. Call lrtOracle.updateRSETHPrice() again.
// 8. Assert: call succeeds — confirming the DoS is resolved only after oracle registration.
```

The revert at step 5 is triggered by:
`updateRSETHPrice` → `_updateRsETHPrice` → `_getTotalEthInProtocol` → `getAssetPrice(newAsset)` → `onlySupportedOracle(newAsset)` → `revert AssetOracleNotSupported()`.

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
