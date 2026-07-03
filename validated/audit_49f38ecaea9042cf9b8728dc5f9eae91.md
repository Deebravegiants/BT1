### Title
Stale `rsETHPrice` Cache After Asset Oracle Update Allows Depositors to Receive Excess rsETH - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.rsETHPrice` is a manually-updated cached exchange rate. When an admin updates an asset's price oracle via `updatePriceOracleFor()`, the `rsETHPrice` cache is not automatically refreshed. During the window between the oracle update and the next `updateRSETHPrice()` call, any depositor can receive more rsETH than their proportional share, diluting existing holders.

### Finding Description

`LRTOracle` stores `rsETHPrice` as a cached value computed from total protocol ETH divided by rsETH supply. It must be explicitly updated by calling `updateRSETHPrice()` (public) or `updateRSETHPriceAsManager()` (manager-only). [1](#0-0) 

When `updatePriceOracleFor(asset, newOracle)` is called, the new oracle immediately affects `getAssetPrice(asset)` (live read), but `rsETHPrice` remains stale: [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` mixes the live oracle price with the stale cached `rsETHPrice`: [3](#0-2) 

If the new oracle returns a higher price for the asset, `getAssetPrice(asset)` increases immediately while `rsETHPrice` remains at its old lower value. The formula `(amount * newHigherAssetPrice) / oldLowerRsETHPrice` mints more rsETH than the depositor's fair share.

The `rsETHPrice` is only updated when `_updateRsETHPrice()` is called, which reads the current oracle prices at that moment: [4](#0-3) 

There is no mechanism to enforce that `rsETHPrice` is synced before `depositAsset()` or `depositETH()` executes. This is the direct analog of the external report's pattern: a state change (`updatePriceOracleFor`) followed by user interaction (`depositAsset`) before the cache is rebuilt (`updateRSETHPrice`).

### Impact Explanation

Existing rsETH holders are diluted. A depositor who acts between `updatePriceOracleFor()` and `updateRSETHPrice()` receives rsETH computed at the stale (lower) price, giving them a larger share of the protocol than they paid for. The excess rsETH comes at the expense of existing holders whose proportional claim on protocol TVL is reduced. This constitutes **theft of unclaimed yield** (High).

**Concrete example:**
- Protocol TVL: 1050 ETH, rsETH supply: 1000, `rsETHPrice` = 1.05 ETH/rsETH
- Admin updates stETH oracle from 1.0 → 1.05 ETH/stETH (true new `rsETHPrice` should be 1.1 ETH/rsETH)
- User deposits 100 stETH before `updateRSETHPrice()` is called:
  - Minted: `(100 × 1.05) / 1.05 = 100 rsETH`
  - Fair amount: `(100 × 1.05) / 1.1 ≈ 95.45 rsETH`
  - Excess: **~4.55 rsETH stolen from existing holders**

### Likelihood Explanation

Oracle updates are routine admin operations (e.g., upgrading oracle contracts, fixing price feeds, adding new LST oracles). The window between `updatePriceOracleFor()` and `updateRSETHPrice()` spans at least one block and typically several. Since `depositAsset()` and `depositETH()` are permissionless, any user monitoring the chain for oracle update transactions can deposit immediately after to exploit the stale price. No special privileges are required beyond being a normal depositor. [5](#0-4) 

### Recommendation

Call `_updateRsETHPrice()` at the end of `updatePriceOracleFor()` to atomically sync the cache whenever the oracle changes:

```solidity
function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
    if (lrtConfig.isSupportedAsset(asset)) {
        UtilLib.checkNonZeroAddress(priceOracle);
    }
    assetPriceOracle[asset] = priceOracle;
    emit AssetPriceOracleUpdate(asset, priceOracle);
    _updateRsETHPrice(); // sync cache immediately
}
```

Alternatively, add a staleness check modifier to `depositAsset()` and `depositETH()` requiring `rsETHPrice` to have been updated within the current block.

### Proof of Concept

1. `LRTOracle.rsETHPrice` = 1.05 ETH/rsETH (last updated at block N).
2. At block N+1, admin calls `LRTOracle.updatePriceOracleFor(stETH, newOracle)` where `newOracle.getAssetPrice(stETH)` returns 1.05 ETH instead of 1.0 ETH. `rsETHPrice` remains 1.05 ETH/rsETH (stale; true value should be ~1.1 ETH/rsETH).
3. At block N+1 (same block or next), user calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
   - `getRsETHAmountToMint` computes: `(100e18 × 1.05e18) / 1.05e18 = 100e18` rsETH minted.
   - Fair amount at correct price: `(100e18 × 1.05e18) / 1.1e18 ≈ 95.45e18` rsETH.
   - User receives **~4.55 rsETH excess**, diluting all existing holders.
4. Admin calls `LRTOracle.updateRSETHPrice()` — cache is now synced, but the excess rsETH has already been minted and cannot be recovered. [2](#0-1) [3](#0-2) [6](#0-5)

### Citations

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

**File:** contracts/LRTOracle.sol (L313-315)
```text
        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
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
