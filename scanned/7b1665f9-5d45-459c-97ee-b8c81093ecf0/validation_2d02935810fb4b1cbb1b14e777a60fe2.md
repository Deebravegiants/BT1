### Title
Chainlink Circuit Breaker Not Checked in `getAssetPrice` Allows Inflated LST Pricing During Depeg — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but never validates the returned price against the Chainlink aggregator's `minAnswer` / `maxAnswer` bounds. If a supported LST asset depegs severely enough to trigger Chainlink's circuit breaker, the oracle returns the capped floor price instead of the true (lower) market price. Depositors can then deposit the devalued asset and receive more rsETH than the asset is worth, stealing value from existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the price from Chainlink and immediately uses it: [1](#0-0) 

The only implicit check is that `uint256(price)` does not underflow (i.e., `price >= 0`). There is no check that `price > aggregator.minAnswer`. When an asset's true market price falls below `minAnswer`, Chainlink's circuit breaker causes `latestRoundData()` to return `minAnswer` — a value higher than the real price — without reverting or signalling an error.

This price flows directly into `LRTOracle.getAssetPrice()`: [2](#0-1) 

Which is used in `LRTDepositPool.getRsETHAmountToMint()` to compute how many rsETH tokens to mint per deposited LST unit: [3](#0-2) 

And is also used in `LRTOracle._getTotalEthInProtocol()` to compute the total ETH backing rsETH (which sets `rsETHPrice`): [4](#0-3) 

The same unchecked Chainlink call exists in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which prices collateral for the RSETH pool: [5](#0-4) 

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield / protocol insolvency.**

When an LST asset (e.g., stETH, cbETH) depegs below Chainlink's `minAnswer`:

1. `ChainlinkPriceOracle.getAssetPrice()` returns `minAnswer` (inflated relative to true price).
2. `getRsETHAmountToMint()` mints rsETH at the inflated rate: `rsethToMint = depositAmount * inflatedPrice / rsETHPrice`.
3. The attacker receives more rsETH than the deposited asset is worth.
4. When `updateRSETHPrice()` is next called, `_getTotalEthInProtocol()` also uses the inflated price, temporarily masking the insolvency — but once the true price is reflected (e.g., after the circuit breaker is lifted), `rsETHPrice` drops, diluting all existing holders.

The `pricePercentageLimit` downside protection in `LRTOracle._updateRsETHPrice()` may eventually pause the protocol, but only after the attacker has already minted and exited. [6](#0-5) 

---

### Likelihood Explanation

**Likelihood: Low.**

This requires a supported LST asset to depeg severely enough to breach Chainlink's `minAnswer`. This is a rare but non-theoretical event (e.g., the LUNA/UST collapse caused similar circuit breaker activations on Chainlink). The protocol operates on Ethereum mainnet where ETH LSTs (stETH, cbETH, etc.) are supported assets, and their Chainlink feeds do have active `minAnswer` values.

---

### Recommendation

In `ChainlinkPriceOracle.getAssetPrice()`, retrieve the aggregator's `minAnswer` and `maxAnswer` and revert if the returned price is outside those bounds:

```solidity
interface IAggregatorWithMinMax {
    function minAnswer() external view returns (int192);
    function maxAnswer() external view returns (int192);
}

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();

    int192 minAnswer = IAggregatorWithMinMax(assetPriceFeed[asset]).minAnswer();
    int192 maxAnswer = IAggregatorWithMinMax(assetPriceFeed[asset]).maxAnswer();
    require(price > minAnswer && price < maxAnswer, "Price outside circuit breaker bounds");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

---

### Proof of Concept

1. Assume stETH is a supported asset with a Chainlink feed whose `minAnswer = 0.5e18` (ETH-denominated).
2. stETH depegs; true market price drops to `0.3e18`.
3. Chainlink circuit breaker activates; `latestRoundData()` returns `0.5e18`.
4. `ChainlinkPriceOracle.getAssetPrice(stETH)` returns `0.5e18` — no revert, no bounds check.
5. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
6. `getRsETHAmountToMint` computes: `rsethToMint = 1000e18 * 0.5e18 / rsETHPrice` — minting as if stETH is worth `0.5 ETH` when it is only worth `0.3 ETH`.
7. Attacker receives ~67% more rsETH than deserved, diluting all existing rsETH holders. [1](#0-0) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```
