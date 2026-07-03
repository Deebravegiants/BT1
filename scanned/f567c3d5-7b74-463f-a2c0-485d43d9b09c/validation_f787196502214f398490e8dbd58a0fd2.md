### Title
Chainlink Price Not Validated Before Use, Enabling rsETH Price Manipulation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and casts the returned `int256 price` directly to `uint256` without checking for non-positive values, stale rounds, or incomplete rounds. This is the direct Chainlink analog of the Pyth oracle validation gap described in the external report. A zero or negative price from a Chainlink circuit-breaker event propagates unchecked into `LRTOracle._getTotalEthInProtocol()`, deflating the computed `rsETHPrice`, which any unprivileged depositor can then exploit to mint excess rsETH.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` performs no input validation on the value returned by `latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

Three validations are absent:
1. **`price <= 0`** — Chainlink feeds can return 0 (circuit-breaker min-price) or a negative value; casting a negative `int256` to `uint256` produces `2^256 - |price|`.
2. **`answeredInRound < roundId`** — detects a stale answer.
3. **`updatedAt == 0`** — detects an incomplete round.

The sister contract `ChainlinkOracleForRSETHPoolCollateral` in the same repo performs all three checks correctly:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L30-32
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle.getAssetPrice()` is consumed in two critical paths:

**Path 1 — rsETH price update:**
`LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported LST and sums the results to compute `totalETHInProtocol`, which directly determines `newRsETHPrice`. [3](#0-2) 

**Path 2 — rsETH minting:**
`LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)` to compute how many rsETH tokens to mint per deposited unit. [4](#0-3) 

### Impact Explanation

**Scenario — Chainlink circuit-breaker returns `price = 0`:**

When a Chainlink feed hits its minimum-price circuit breaker it can return `0`. `uint256(0) * 1e18 / decimals = 0`, so `getAssetPrice` returns `0` for that LST.

1. `_getTotalEthInProtocol()` sums asset values; the affected LST contributes `0 ETH` regardless of its true balance, understating `totalETHInProtocol`.
2. `newRsETHPrice = (totalETHInProtocol - fee) / rsethSupply` is deflated below the true backing ratio.
3. `updateRSETHPrice()` is **public** — any caller can commit this deflated price to storage (`rsETHPrice`). [5](#0-4) 

4. With `rsETHPrice` deflated, `getRsETHAmountToMint` for a *different* (correctly-priced) asset yields:
   `rsethAmountToMint = (amount * correctAssetPrice) / deflatedRsETHPrice` — more rsETH than deserved.
5. The attacker deposits the correctly-priced asset, receives excess rsETH, and redeems at the recovered price — stealing value from existing rsETH holders.

The `pricePercentageLimit` downside-pause guard only fires when `pricePercentageLimit > 0`; its default is `0`, leaving the guard inactive until an admin explicitly sets it. [6](#0-5) 

**Impact rating: High** — theft of yield/value from existing rsETH holders proportional to the TVL of the affected LST.

### Likelihood Explanation

Chainlink circuit-breaker events (returning `0` or a min/max sentinel) are documented and have occurred on mainnet (e.g., LUNA crash, stETH depeg). The attack requires no special permissions: `updateRSETHPrice()` is public and `depositAsset()` is open to any user. An attacker only needs to observe the on-chain Chainlink answer and act within the same block or shortly after.

### Recommendation

Add the following checks inside `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (price <= 0)                  revert InvalidPrice();
if (updatedAt == 0)              revert IncompleteRound();
if (answeredInRound < roundId)   revert StalePrice();
// Optionally: if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
``` [1](#0-0) 

### Proof of Concept

1. Chainlink feed for LST asset `X` hits its circuit-breaker floor and returns `price = 0`.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(X)` → returns `0`; asset `X`'s TVL is excluded from the sum.
4. `newRsETHPrice` is deflated (e.g., true price 1.05 ETH, computed price 0.90 ETH if `X` is 15% of TVL).
5. `rsETHPrice` is written to storage at the deflated value.
6. Attacker calls `depositAsset(Y, amount, 0, "")` for a correctly-priced asset `Y`.
7. `getRsETHAmountToMint` = `(amount * getAssetPrice(Y)) / rsETHPrice` → mints ~16.7% more rsETH than fair value.
8. Chainlink feed recovers; attacker initiates withdrawal and redeems excess rsETH at the true backing ratio, extracting value from all other rsETH holders. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L273-274)
```text
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
