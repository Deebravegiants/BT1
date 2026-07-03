### Title
Newly Added Supported Asset Without Price Oracle Freezes `updateRSETHPrice()`, Enabling Deposits at Stale Rate — (`contracts/LRTOracle.sol`)

---

### Summary

When a new asset is added to `LRTConfig` via `addNewSupportedAsset()` but before its price oracle is registered in `LRTOracle` via `updatePriceOracleFor()`, every call to `updateRSETHPrice()` reverts. The stored `rsETHPrice` becomes permanently stale for the duration of this window. Because `LRTDepositPool.getRsETHAmountToMint()` reads the stale stored price directly, depositors can mint rsETH at an outdated (lower) rate, diluting existing rsETH holders of accrued yield.

---

### Finding Description

`LRTConfig.addNewSupportedAsset()` pushes a new asset into `supportedAssetList` with no requirement that a corresponding price oracle exists in `LRTOracle`:

```solidity
// LRTConfig.sol L99-L117
function addNewSupportedAsset(address asset, uint256 depositLimit)
    external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
    _addNewSupportedAsset(asset, depositLimit);
}
// _addNewSupportedAsset sets isSupportedAsset[asset]=true and pushes to supportedAssetList
// — no oracle check whatsoever
```

`LRTOracle._getTotalEthInProtocol()` iterates over every entry in `supportedAssetList` and calls `getAssetPrice(asset)` for each:

```solidity
// LRTOracle.sol L336-L343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);   // <-- reverts if oracle not set
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
```

`getAssetPrice()` is guarded by `onlySupportedOracle`, which hard-reverts when `assetPriceOracle[asset] == address(0)`:

```solidity
// LRTOracle.sol L40-L44
modifier onlySupportedOracle(address asset) {
    if (assetPriceOracle[asset] == address(0)) {
        revert AssetOracleNotSupported();
    }
    _;
}
```

Because `_getTotalEthInProtocol()` is called unconditionally inside `_updateRsETHPrice()`, the entire `updateRSETHPrice()` (and `updateRSETHPriceAsManager()`) call reverts for every caller until the oracle is registered.

Meanwhile, `LRTDepositPool.getRsETHAmountToMint()` reads the **stored** `rsETHPrice` directly — it never triggers a price refresh:

```solidity
// LRTDepositPool.sol L519-L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

So deposits continue to execute against the last committed (now stale) price.

---

### Impact Explanation

Staking rewards accrue continuously, meaning the true rsETH/ETH rate rises over time. While `updateRSETHPrice()` is broken, the stored `rsETHPrice` is lower than the true rate. Any depositor who calls `depositAsset()` or `depositETH()` during this window receives **more rsETH than they are entitled to** (numerator `getAssetPrice(asset)` is live; denominator `rsETHPrice` is stale-low). The excess rsETH is minted at the expense of existing holders whose accrued yield is diluted — a direct theft of unclaimed yield.

**Impact**: High — theft of unclaimed yield from all existing rsETH holders.

---

### Likelihood Explanation

`addNewSupportedAsset()` requires `TIME_LOCK_ROLE` (a timelock contract), while `updatePriceOracleFor()` requires `onlyLRTAdmin`. These are structurally separate transactions. The timelock execution itself creates a **guaranteed non-zero window** between the asset becoming live in `supportedAssetList` and the admin separately calling `updatePriceOracleFor()`. Any block mined in that window where staking rewards have accrued since the last price update is exploitable by any depositor.

**Likelihood**: Medium — normal governance operations create the window without any admin error or compromise.

---

### Recommendation

1. **Atomic registration**: Extend `addNewSupportedAsset()` (or a wrapper) to atomically call `LRTOracle.updatePriceOracleFor()` in the same transaction, ensuring no asset ever enters `supportedAssetList` without a live oracle.

2. **Graceful skip**: In `_getTotalEthInProtocol()`, skip assets whose `assetPriceOracle` is `address(0)` rather than reverting, so a missing oracle degrades gracefully instead of freezing all price updates.

3. **Deposit guard**: In `depositAsset()` / `depositETH()`, call `updateRSETHPrice()` (or assert it does not revert) before minting, so deposits cannot proceed against a stale price.

---

### Proof of Concept

1. Protocol is live; `rsETHPrice` was last updated at `T=0` (e.g., `1.02 ETH`).
2. At `T=1`, admin's timelock executes `LRTConfig.addNewSupportedAsset(newLST, limit)`. `newLST` is now in `supportedAssetList`. No oracle is set yet in `LRTOracle`.
3. At `T=2`, staking rewards push the true rsETH rate to `1.025 ETH`, but `rsETHPrice` is still `1.02 ETH` because every call to `updateRSETHPrice()` reverts at `getAssetPrice(newLST)` → `AssetOracleNotSupported`.
4. Attacker calls `depositAsset(stETH, 100e18, 0, "")`. `getRsETHAmountToMint` computes `100e18 * 1e18 / 1.02e18 ≈ 98.04 rsETH` instead of the correct `≈ 97.56 rsETH`. Attacker receives ~0.48 rsETH extra per 100 stETH deposited.
5. At `T=3`, admin calls `updatePriceOracleFor(newLST, oracle)`. `updateRSETHPrice()` now succeeds and the price jumps to `1.025 ETH`, but the dilution already occurred. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
