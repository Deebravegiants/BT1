### Title
Hardcoded 18-Decimal Assumption in `_getTotalEthInProtocol()` Causes Incorrect rsETH Price and Share Mis-Accounting for Non-18 Decimal Assets - (File: contracts/LRTOracle.sol)

---

### Summary
`LRTOracle._getTotalEthInProtocol()` unconditionally applies `mulWad` (which divides by 1e18) to raw token balances, hardcoding the assumption that every supported asset has 18 decimals. If a non-18 decimal token is ever added as a supported asset, the TVL calculation is wrong by a factor of `10^(18 − decimals)`, producing a severely incorrect `rsETHPrice`. The same assumption is repeated in `LRTConverter` and `LRTDepositPool` swap helpers. No on-chain guard prevents a non-18 decimal token from being registered.

---

### Finding Description

**Root cause — `LRTOracle._getTotalEthInProtocol()` (lines 336–348):**

```solidity
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    // assetER is in 1e18 precision (1.0 = 1e18)
    uint256 assetER = getAssetPrice(asset);
    // totalAssetAmt is in 1e18 precision (standard token decimals)  ← hardcoded assumption
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

    totalETHInProtocol += totalAssetAmt.mulWad(assetER);   // mulWad = x * y / 1e18
    ...
}
```

`getTotalAssetDeposits` returns the raw ERC-20 balance in the token's native decimals. `mulWad` divides by 1e18. For an 18-decimal token the math is correct. For a 6-decimal token (e.g. USDC):

| Variable | 18-decimal token | 6-decimal token |
|---|---|---|
| `totalAssetAmt` | `1000 × 1e18` | `1000 × 1e6 = 1e9` |
| `assetER` | `~1e18` | `~4e14` (0.0004 ETH/USDC) |
| `mulWad` result | `~1000 × 1e18` ✓ | `1e9 × 4e14 / 1e18 = 4e5 wei` ✗ |
| Correct ETH value | `~1000 ETH` | `0.4 ETH = 4e17 wei` |

The result is **1e12 times smaller** than the true ETH value, causing `rsETHPrice` to be understated.

**Same assumption repeated in:**

- `LRTConverter.transferAssetFromDepositPool()` line 140:
  `ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;`
- `LRTConverter.transferAssetToDepositPool()` line 160:
  `uint256 assetValue = (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;`
- `LRTDepositPool.getSwapAssetForETHReturnAmount()` line 560:
  `return lrtOracle.getAssetPrice(fromAsset) * fromAssetAmount / 1e18;`
- `LRTDepositPool.getRsETHAmountToMint()` line 520 (via `getAssetPrice`):
  `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();`

**No guard exists.** `LRTConfig` accepts any ERC-20 as a supported asset. `LRTOracle.updatePriceOracleForValidated()` only checks that the oracle price is between `1e16` and `1e19`; it does not check the token's `decimals()`.

---

### Impact Explanation

If a non-18 decimal token is added as a supported asset:

1. **Depositors receive wrong rsETH amounts.** For 1000 USDC (6 decimals, worth 0.4 ETH), `getRsETHAmountToMint` returns `1e9 × 4e14 / 1e18 = 4e5 wei` of rsETH instead of `4e17 wei` — a factor of 1e12 too few. The depositor's funds are effectively locked with no recoverable rsETH.

2. **rsETH price is understated.** `_getTotalEthInProtocol()` omits the true ETH value of the non-18 decimal token, causing `rsETHPrice` to be lower than it should be. All rsETH holders are diluted relative to the true TVL.

3. **Price protection may trigger a protocol pause.** If the understated TVL causes `newRsETHPrice` to fall below `highestRsethPrice` by more than `pricePercentageLimit`, `LRTOracle._updateRsETHPrice()` pauses both `LRTDepositPool` and `LRTWithdrawalManager`, temporarily freezing all user funds.

**Impact classification:** Low (contract fails to deliver promised returns to depositors of non-18 decimal tokens) escalating to Medium (temporary freezing of funds via price-protection pause).

---

### Likelihood Explanation

Medium-Low. The protocol currently supports only ETH-based LSTs (stETH, ETHx, rETH, swETH, sfrxETH, ETH), all of which have 18 decimals. However:

- No on-chain enforcement prevents a non-18 decimal token from being registered via `LRTConfig.addNewSupportedAsset()`.
- The protocol's admin could legitimately add a new collateral type (e.g., a wrapped BTC or stablecoin) in a future upgrade without realising the decimal assumption is hardcoded throughout the accounting layer.
- The code comment `// totalAssetAmt is in 1e18 precision (standard token decimals)` shows the assumption is implicit and undocumented as a constraint.

---

### Recommendation

1. In `_getTotalEthInProtocol()`, normalize `totalAssetAmt` to 18 decimals before applying `mulWad`:
   ```solidity
   uint8 assetDecimals = IERC20Metadata(asset).decimals();
   uint256 normalizedAmt = totalAssetAmt * 10 ** (18 - assetDecimals);
   totalETHInProtocol += normalizedAmt.mulWad(assetER);
   ```
2. Apply the same normalization in `LRTConverter.transferAssetFromDepositPool/transferAssetToDepositPool` and `LRTDepositPool.getSwapAssetForETHReturnAmount`.
3. Add an on-chain guard in `LRTConfig.addNewSupportedAsset()` (or in `LRTOracle.updatePriceOracleFor`) that rejects tokens whose `decimals()` is not 18, or explicitly documents and enforces the 18-decimal invariant.

---

### Proof of Concept

**Scenario:** Admin adds USDC (6 decimals) as a supported asset with a Chainlink USDC/ETH price feed.

1. User calls `LRTDepositPool.depositAsset(USDC, 1000e6, 0, "")`.
2. `getRsETHAmountToMint(USDC, 1000e6)` is called:
   - `assetPrice = ChainlinkPriceOracle.getAssetPrice(USDC)` → `40000 * 1e18 / 1e8 = 4e14` (0.0004 ETH/USDC, feed has 8 decimals).
   - `rsETHPrice ≈ 1e18`.
   - `rsethAmountToMint = 1000e6 * 4e14 / 1e18 = 4e5 wei` of rsETH.
   - Correct value: `1000 * 0.0004 ETH = 0.4 ETH = 4e17 wei` of rsETH.
   - **User receives 1e12× fewer rsETH than owed.**
3. `LRTOracle.updateRSETHPrice()` is called:
   - `_getTotalEthInProtocol()` adds `mulWad(1000e6, 4e14) = 4e5 wei` for USDC instead of `4e17 wei`.
   - `rsETHPrice` is understated; if the discrepancy exceeds `pricePercentageLimit`, the protocol pauses. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L100-108)
```text
    /// @param asset asset address for which oracle price needs to be added/updated
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
    }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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
```

**File:** contracts/LRTConverter.sol (L136-143)
```text
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
    }
```

**File:** contracts/LRTConverter.sol (L157-165)
```text
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);
        uint256 assetValue = (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        // Set to 0 if assetValue exceeds ethValueInWithdrawal, otherwise subtract assetValue
        ethValueInWithdrawal = ethValueInWithdrawal > assetValue ? ethValueInWithdrawal - assetValue : 0;

        IERC20(_asset).safeTransfer(lrtDepositPoolAddress, _amount);
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

**File:** contracts/LRTDepositPool.sol (L549-561)
```text
    function getSwapAssetForETHReturnAmount(
        address fromAsset,
        uint256 fromAssetAmount
    )
        public
        view
        returns (uint256 returnAmount)
    {
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        return lrtOracle.getAssetPrice(fromAsset) * fromAssetAmount / 1e18;
    }
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```
