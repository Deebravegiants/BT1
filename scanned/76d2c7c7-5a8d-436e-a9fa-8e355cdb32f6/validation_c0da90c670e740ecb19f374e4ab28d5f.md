### Title
Missing price oracle enforcement on `addNewSupportedAsset` causes permanent `updateRSETHPrice` DoS — (File: contracts/LRTOracle.sol)

### Summary
`LRTConfig.addNewSupportedAsset()` pushes an asset into `supportedAssetList` with no requirement that a price oracle be registered for it in `LRTOracle`. `LRTOracle._getTotalEthInProtocol()` iterates every entry in `supportedAssetList` and calls `getAssetPrice(asset)`, which reverts with `AssetOracleNotSupported()` for any asset whose `assetPriceOracle` mapping is `address(0)`. This permanently breaks `updateRSETHPrice()` until admin intervention, leaving the rsETH exchange rate stale and disabling the protocol's price-protection auto-pause mechanism.

### Finding Description

`LRTConfig._addNewSupportedAsset()` unconditionally pushes the new asset into `supportedAssetList` and sets its deposit limit, but performs no check that a price oracle exists in `LRTOracle`: [1](#0-0) 

The public entry point `addNewSupportedAsset()` (gated by `TIME_LOCK_ROLE`) calls this private function: [2](#0-1) 

Setting the oracle is a completely separate, independent admin call in `LRTOracle`: [3](#0-2) 

`_getTotalEthInProtocol()` iterates the full `supportedAssetList` and calls `getAssetPrice(asset)` for every entry: [4](#0-3) 

`getAssetPrice()` carries the `onlySupportedOracle` modifier, which reverts if `assetPriceOracle[asset] == address(0)`: [5](#0-4) [6](#0-5) 

`_getTotalEthInProtocol()` is called exclusively from `_updateRsETHPrice()`, which is the body of the public `updateRSETHPrice()`: [7](#0-6) [8](#0-7) 

The structural inconsistency is identical to the Aragon report: the list (`supportedAssetList`) is populated by one operation (`addNewSupportedAsset`) while the required condition (oracle registration) is fulfilled by a separate, independent operation (`updatePriceOracleFor`). There is no atomicity guarantee and no enforcement at addition time.

### Impact Explanation

While the asset is in `supportedAssetList` without a registered oracle, every call to `updateRSETHPrice()` reverts. Consequences:

1. **Stale rsETH price** — `rsETHPrice` is frozen at its last value. All deposits (`depositAsset`, `depositETH`) and withdrawals (`initiateWithdrawal`, `instantWithdrawal`) use this stale rate, causing users to receive incorrect rsETH or asset amounts.
2. **Price-protection auto-pause disabled** — `_updateRsETHPrice()` contains the downside-protection logic that auto-pauses `LRTDepositPool` and `LRTWithdrawalManager` on excessive price drops. With `updateRSETHPrice()` reverting, this safety mechanism is silently inoperative.
3. **Fee minting broken** — Protocol fee accrual via rsETH minting to treasury is halted.

Impact: **Medium — Temporary freezing of funds** (stale price causes incorrect minting/burning for all users until admin remediation).

### Likelihood Explanation

The `addNewSupportedAsset` path is gated by `TIME_LOCK_ROLE` and goes through a timelock. The oracle registration (`updatePriceOracleFor`) is a separate admin call with no enforced ordering. Any deployment sequence where the asset is added before its oracle is configured — including the window between timelock execution and oracle setup — activates the DoS. This is a realistic operational scenario, not a malicious one, and mirrors exactly the ordering problem described in the Aragon report.

### Recommendation

Enforce oracle registration atomically at asset-addition time. Either:

1. Require that `LRTOracle.assetPriceOracle[asset] != address(0)` before `_addNewSupportedAsset` completes (analogous to the Aragon fix of checking `tap.isTapped(token)` before adding to `toReset`), or
2. Accept an oracle address as a parameter to `addNewSupportedAsset` and register it in the same transaction.

### Proof of Concept

1. Admin calls `LRTConfig.addNewSupportedAsset(newAsset, depositLimit)` via `TIME_LOCK_ROLE`. `newAsset` is pushed into `supportedAssetList`. `LRTOracle.assetPriceOracle[newAsset]` remains `address(0)`.
2. Any caller (including a regular user) calls `LRTOracle.updateRSETHPrice()`.
3. Execution reaches `_getTotalEthInProtocol()` → iterates `supportedAssetList` → hits `newAsset` → calls `getAssetPrice(newAsset)` → `onlySupportedOracle` fires → reverts with `AssetOracleNotSupported()`.
4. `updateRSETHPrice()` is permanently broken. `rsETHPrice` is stale. All subsequent deposits and withdrawals execute at the frozen rate. The price-drop auto-pause is inoperative.
5. Recovery requires admin to call `updatePriceOracleFor(newAsset, oracle)` or `removeSupportedAsset(newAsset, index)`.

### Citations

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
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

**File:** contracts/LRTOracle.sol (L214-232)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
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
