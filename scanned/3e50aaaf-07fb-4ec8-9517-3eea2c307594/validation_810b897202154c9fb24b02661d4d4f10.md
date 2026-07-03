### Title
Adding a Supported Asset Without a Price Oracle Permanently Freezes `updateRSETHPrice()`, Breaking Protocol Fee Minting and Share Accounting - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTConfig.addNewSupportedAsset()` registers a new asset into `supportedAssetList` without requiring a corresponding price oracle to be set in `LRTOracle`. Once any rsETH supply exists, every subsequent call to `updateRSETHPrice()` iterates over all supported assets and calls `getAssetPrice()` for each. If any asset lacks an oracle entry, `getAssetPrice()` reverts with `AssetOracleNotSupported`, permanently freezing the rsETH price, breaking protocol fee minting, and causing stale-price share mis-accounting for all depositors.

---

### Finding Description

`LRTConfig.addNewSupportedAsset()` only validates that the asset address is non-zero and the deposit limit is non-zero before pushing the asset into `supportedAssetList`: [1](#0-0) 

There is no requirement that a price oracle be registered in `LRTOracle` for the new asset at the time of addition.

`LRTOracle.updateRSETHPrice()` is a public function that calls `_updateRsETHPrice()`, which — when `rsethSupply > 0` — calls `_getTotalEthInProtocol()`: [2](#0-1) 

`_getTotalEthInProtocol()` iterates over every asset in `supportedAssetList` and calls `getAssetPrice(asset)` for each: [3](#0-2) 

`getAssetPrice()` is guarded by `onlySupportedOracle`, which reverts with `AssetOracleNotSupported` if `assetPriceOracle[asset] == address(0)`: [4](#0-3) [5](#0-4) 

Once an oracle-less asset is in `supportedAssetList` and rsETH supply is non-zero, every call to `updateRSETHPrice()` reverts. The stored `rsETHPrice` is frozen at its last value. All deposits then use this stale price: [6](#0-5) 

The early-return path at line 218–222 (when `rsethSupply == 0`) bypasses `_getTotalEthInProtocol()`, so the bug only manifests after the first deposit is made. [7](#0-6) 

---

### Impact Explanation

Three concrete harms result:

1. **Permanent freezing of unclaimed yield (protocol fees)**: Protocol fee minting occurs inside `_updateRsETHPrice()` at lines 299–308. Since `_updateRsETHPrice()` always reverts when supply > 0, the treasury never receives its fee share of staking rewards. This is a permanent loss of yield for the protocol. [8](#0-7) 

2. **Share mis-accounting for depositors**: `getRsETHAmountToMint()` divides by the frozen `rsETHPrice`. As actual TVL grows from EigenLayer rewards, the true rsETH/ETH rate rises above the frozen value. New depositors receive more rsETH than they are entitled to, diluting existing holders — a form of fund mis-accounting. [6](#0-5) 

3. **Price-based pause protection disabled**: The downside protection that auto-pauses the protocol on a large price drop (lines 270–281) never triggers, removing a critical safety mechanism. [9](#0-8) 

---

### Likelihood Explanation

`addNewSupportedAsset()` and `updatePriceOracleFor()` are separate governance transactions. A timelock admin adding a new LST in one proposal and omitting the oracle registration step — or executing the two steps out of order — is a realistic operational mistake, directly analogous to the M-26 scenario of adding a property without items. The public `updateRSETHPrice()` function is called by keeper bots and any user, so the revert is immediately observable and persistent.

---

### Recommendation

**Short term**: In `LRTConfig.addNewSupportedAsset()`, require that a valid price oracle is already registered in `LRTOracle` for the asset before it is added to `supportedAssetList`. Alternatively, accept the oracle address as a parameter and atomically register it.

**Long term**: After adding a new asset and its oracle, call `updateRSETHPrice()` as part of the same governance proposal and verify it succeeds without reverting before the proposal is considered complete.

---

### Proof of Concept

```
1. Protocol is live; rsETHPrice = 1 ether (set on first updateRSETHPrice() call when supply was 0).
   rsETH supply is now > 0 (users have deposited).

2. Admin calls LRTConfig.addNewSupportedAsset(newLST, depositLimit).
   No oracle is registered in LRTOracle for newLST (assetPriceOracle[newLST] == address(0)).

3. Keeper bot (or any user) calls LRTOracle.updateRSETHPrice().
   → _updateRsETHPrice() → rsethSupply > 0, so _getTotalEthInProtocol() is called
   → loop reaches newLST → getAssetPrice(newLST) → onlySupportedOracle reverts: AssetOracleNotSupported
   → updateRSETHPrice() reverts. rsETHPrice stays frozen at 1 ether.

4. EigenLayer staking rewards accrue. True rsETH/ETH rate rises to, say, 1.05 ether.
   rsETHPrice is still 1 ether.

5. New depositor calls depositAsset(stETH, 1e18, 0, "").
   → getRsETHAmountToMint: (1e18 * 1e18) / 1e18 = 1e18 rsETH minted.
   Correct amount at true rate: (1e18 * 1e18) / 1.05e18 ≈ 0.952e18 rsETH.
   Depositor receives ~5% excess rsETH, diluting all existing holders.

6. Protocol fee is never minted. Treasury receives 0 yield indefinitely.

7. Fix requires a new governance proposal to call LRTOracle.updatePriceOracleFor(newLST, oracle).
```

### Citations

**File:** contracts/LRTConfig.sol (L99-117)
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

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L270-281)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
