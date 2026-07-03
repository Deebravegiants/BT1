### Title
`_getTotalEthInProtocol()` Silently Assumes 18-Decimal Precision for All Supported Assets, Corrupting rsETH Price and Minting When a Non-18-Decimal Asset Is Added - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` treats every supported asset's raw on-chain balance as if it were already in 18-decimal (WAD) precision. `LRTDepositPool.getRsETHAmountToMint()` makes the same assumption. If a token with fewer than 18 decimals is ever added as a supported asset via `LRTConfig.addNewSupportedAsset()`, both the rsETH price and the rsETH minting amount will be computed with a magnitude error proportional to `10^(18 - tokenDecimals)`, corrupting all subsequent protocol accounting.

---

### Finding Description

`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset and computes the protocol's total ETH value:

```solidity
// totalAssetAmt is in 1e18 precision (standard token decimals)   ← comment is wrong
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [1](#0-0) 

`getTotalAssetDeposits` returns the raw ERC-20 balance of the asset (e.g. `IERC20(asset).balanceOf(...)`) in the token's **native** decimals, not normalized to 1e18. [2](#0-1) 

`mulWad(x, y)` computes `x * y / 1e18`. When `totalAssetAmt` is in 6 decimals (e.g. 1 USDC = `1_000_000`) and `assetER` is in 1e18 precision, the result is `1_000_000` instead of the correct `1e18`. The TVL is understated by `10^12`. [3](#0-2) 

The same assumption propagates into `getRsETHAmountToMint`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [4](#0-3) 

For a 6-decimal asset, `amount = 1_000_000`, `getAssetPrice = 1e18`, `rsETHPrice = 1e18` → `rsethAmountToMint = 1_000_000` instead of `1e18`. The depositor is under-minted by `10^12`.

After `updateRSETHPrice()` runs with the corrupted TVL, `rsETHPrice` collapses to `1` (wei), causing the **next** ETH depositor to receive `1e36` rsETH for 1 ETH. The subsequent price update then drives `rsETHPrice` to near-zero, permanently freezing all funds in the protocol.

New assets are added via:

```solidity
function addNewSupportedAsset(address asset, uint256 depositLimit)
    external onlyRole(LRTConstants.TIME_LOCK_ROLE) { ... }
``` [5](#0-4) 

No decimal check is performed anywhere in `_addNewSupportedAsset`. [6](#0-5) 

---

### Impact Explanation

Once a non-18-decimal asset is added and the first deposit occurs:

1. `rsETHPrice` is driven to near-zero by the understated TVL.
2. Subsequent ETH depositors receive astronomically over-minted rsETH.
3. The next `updateRSETHPrice()` call drives `rsETHPrice` to effectively `0`.
4. All withdrawal payouts (`request.rsETHUnstaked * rsETHPrice / assetPrice`) return `0`.
5. All user funds — both the non-18-decimal asset and any ETH deposited after step 1 — are permanently frozen in the protocol.

**Impact: Critical — Permanent freezing of funds / Protocol insolvency.**

---

### Likelihood Explanation

The trigger is a governance action (`TIME_LOCK_ROLE`) to add a non-18-decimal LST or yield-bearing token. The current supported set (stETH, ETHx, native ETH) is all 18-decimal, but the protocol is explicitly designed to be extensible. No guard in `addNewSupportedAsset` or `updatePriceOracleFor` rejects non-18-decimal tokens. A future integration (e.g., a rebasing token with 6 or 8 decimals) would silently trigger the corruption. **Likelihood: Low** (requires a governance decision), but the design flaw is latent and unguarded.

---

### Recommendation

Normalize `totalAssetAmt` to 18-decimal precision before multiplying by the exchange rate in `_getTotalEthInProtocol()`:

```solidity
uint8 assetDecimals = IERC20Metadata(asset).decimals();
uint256 normalizedAmt = totalAssetAmt * (10 ** (18 - assetDecimals));
totalETHInProtocol += normalizedAmt.mulWad(assetER);
```

Apply the same normalization in `getRsETHAmountToMint()` before computing `rsethAmountToMint`. Alternatively, enforce at `addNewSupportedAsset` time that only 18-decimal tokens are accepted.

---

### Proof of Concept

**Setup**: Protocol has 1 ETH deposited; rsETH supply = 1e18; rsETHPrice = 1e18.

1. Admin calls `addNewSupportedAsset(USDC_6DEC, limit)` and `updatePriceOracleFor(USDC_6DEC, oracle_returning_1e18)`.
2. User A calls `depositAsset(USDC_6DEC, 1_000_000, 0, "")` (1 USDC).
   - `getRsETHAmountToMint` → `1_000_000 * 1e18 / 1e18 = 1_000_000` rsETH minted (correct: 1e18).
3. `updateRSETHPrice()` is called.
   - `_getTotalEthInProtocol()` → ETH: 1e18, USDC: `1_000_000 * 1e18 / 1e18 = 1_000_000` → total ≈ 1e18 + 1_000_000.
   - rsETH supply = 1e18 +

### Citations

**File:** contracts/LRTOracle.sol (L338-343)
```text
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/utils/WadMath.sol (L17-19)
```text
    function mulWad(uint256 x, uint256 y) internal pure returns (uint256 z) {
        z = x.mulDiv(y, WAD);
    }
```

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
