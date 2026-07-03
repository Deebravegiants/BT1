### Title
Chainlink Aggregator `minAnswer`/`maxAnswer` Circuit Breaker Not Validated in `ChainlinkPriceOracle` — Inflated LST Price Enables rsETH Over-Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` with no validation of the aggregator's built-in `minAnswer`/`maxAnswer` circuit breaker bounds. If a supported LST asset (stETH, rETH, etc.) crashes in value and the Chainlink aggregator hits its `minAnswer` floor, the oracle silently returns the floor price instead of the true (lower) price. Any depositor can then deposit the devalued LST and receive rsETH minted at the inflated floor price, directly stealing value from all existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the price with a bare `latestRoundData()` call:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no check that `price` is within the aggregator's `minAnswer`–`maxAnswer` band. Chainlink aggregators have a built-in circuit breaker: when the real market price falls below `minAnswer`, the aggregator continues to report `minAnswer` rather than the true price. The contract has no staleness check either (`updatedAt` is discarded entirely).

This price is consumed by `LRTOracle.getAssetPrice()`: [2](#0-1) 

Which is called in two critical paths:

1. **Deposit minting** — `LRTDepositPool.getRsETHAmountToMint()` uses `lrtOracle.getAssetPrice(asset)` to compute how many rsETH tokens to mint per unit of deposited LST: [3](#0-2) 

2. **TVL accounting** — `LRTOracle._getTotalEthInProtocol()` multiplies each asset's total deposits by `getAssetPrice(asset)` to compute the protocol's total ETH value, which drives the rsETH price update: [4](#0-3) 

---

### Impact Explanation

**Critical — Direct theft of user funds / protocol insolvency.**

If a supported LST (e.g., stETH) crashes to, say, 0.5 ETH but the Chainlink aggregator's `minAnswer` is 0.95 ETH, the oracle reports 0.95 ETH. A depositor who deposits 1,000 stETH (true value: 500 ETH) receives rsETH minted as if they deposited 950 ETH worth of value. The excess ~450 ETH worth of rsETH is extracted from the pool, diluting every existing rsETH holder. This is the exact mechanism that caused the Venus/LUNA incident. The `_getTotalEthInProtocol()` path also overstates TVL, causing `rsETHPrice` to be set too high, compounding the damage.

---

### Likelihood Explanation

**Medium-High.** Chainlink aggregators for LST/ETH pairs (e.g., stETH/ETH) do have non-trivial `minAnswer` values. A severe depeg event (smart contract exploit in an LST, slashing cascade, or liquidity crisis) is a realistic tail risk for any LST. The attack requires no special permissions — any unprivileged depositor can call `depositAsset()` during the window when the aggregator is clamped at `minAnswer`.

---

### Recommendation

Add `minAnswer`/`maxAnswer` bounds validation in `ChainlinkPriceOracle.getAssetPrice()`, and also add a staleness check:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    // Staleness check
    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();

    // Circuit breaker bounds check
    IChainlinkAggregator aggregator = IChainlinkAggregator(address(priceFeed));
    int192 minAnswer = aggregator.minAnswer();
    int192 maxAnswer = aggregator.maxAnswer();
    if (price <= minAnswer || price >= maxAnswer) revert PriceOutOfBounds();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Assume stETH/ETH Chainlink feed has `minAnswer = 0.95e18` (a realistic value).
2. A slashing event causes stETH to trade at 0.50 ETH on-chain.
3. Chainlink aggregator hits its circuit breaker and reports `0.95e18` instead of `0.50e18`.
4. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
5. `getRsETHAmountToMint` computes: `(1000e18 * 0.95e18) / rsETHPrice` — using the inflated price.
6. Attacker receives rsETH worth ~950 ETH, but only deposited assets worth ~500 ETH.
7. The ~450 ETH difference is extracted from existing rsETH holders' share of the pool.
8. `updateRSETHPrice()` subsequently calls `_getTotalEthInProtocol()`, which also uses the inflated price, setting `rsETHPrice` too high and masking the insolvency until the aggregator recovers. [5](#0-4) [6](#0-5) [7](#0-6)

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
