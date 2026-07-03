### Title
Missing Staleness Check in `ChainlinkPriceOracle` Allows rsETH Minting at Stale LST Prices — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` fetches Chainlink price data but performs **no staleness validation** on the returned round data. A stale price — one that no longer reflects the true market value of an LST — is silently accepted and used to compute how much rsETH to mint. This is the direct analog to the Aloe IV underestimation bug: just as Aloe's formula could return a systematically incorrect rate with no on-chain correction mechanism, this oracle can return an outdated rate with no on-chain rejection mechanism, leading to incorrect rsETH issuance.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all metadata fields (`roundId`, `startedAt`, `updatedAt`, `answeredInRound`) that are needed to verify freshness:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();          // ← all metadata ignored
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

Contrast this with `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which is used for the L2 pool collateral oracle and **does** validate staleness:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The stale price returned by `ChainlinkPriceOracle.getAssetPrice()` flows into two critical paths:

**Path 1 — rsETH minting rate:**
`LRTDepositPool.getRsETHAmountToMint()` divides the asset's stale price by `rsETHPrice` to determine how many rsETH tokens to issue per unit of deposited LST. [3](#0-2) 

**Path 2 — Protocol TVL and rsETH price update:**
`LRTOracle._getTotalEthInProtocol()` multiplies each asset's total balance by its stale oracle price to compute the protocol's total ETH value, which then sets `rsETHPrice`. [4](#0-3) 

If a supported LST (stETH, rETH, ETHx, sfrxETH, swETH) depegs while the Chainlink feed is stale at the pre-depeg price, the protocol continues to mint rsETH as if the LST is worth its old, higher value. There is no on-chain mechanism to reject or correct the stale price — exactly the asymmetry described in the Aloe report, where there is a mechanism to push the rate in one direction but not the other.

---

### Impact Explanation

An attacker who deposits a depegged LST while the Chainlink feed is stale receives rsETH calculated at the inflated pre-depeg price. When the oracle eventually updates and `rsETHPrice` is recalculated at the true lower TVL, the attacker's rsETH is worth more than what they deposited. The loss is borne by all existing rsETH holders through dilution of the backing per share. In a severe depeg (e.g., 10–20% drop), this constitutes direct theft of user funds at the protocol level.

**Impact: Critical** — direct theft of funds from existing rsETH holders via share dilution.

---

### Likelihood Explanation

Chainlink feeds have heartbeat intervals (e.g., 1 hour for ETH/stETH) and deviation thresholds. During periods of network congestion, oracle keeper failures, or rapid price movement, feeds can lag significantly. LST depeg events are not hypothetical — stETH traded at a ~7% discount to ETH in June 2022. The combination of a stale feed and a depeg event is a realistic, historically observed scenario.

**Likelihood: Medium** — requires a Chainlink feed to be stale during an LST depeg, both of which have occurred independently.

---

### Recommendation

Apply the same staleness checks used in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optionally: if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a configurable `maxStaleness` parameter per asset, since different Chainlink feeds have different heartbeat intervals.

---

### Proof of Concept

1. The Chainlink stETH/ETH feed last updated at price `1.05e18` (1.05 ETH per stETH).
2. stETH depegs to `0.95 ETH` on the market due to a slashing event.
3. The Chainlink feed has not yet updated (within its heartbeat window, or keeper is delayed).
4. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
5. `getRsETHAmountToMint` computes: `(1000e18 * 1.05e18) / rsETHPrice` — using the stale `1.05e18` price.
6. Attacker receives rsETH priced as if they deposited 1050 ETH worth of value, when they only deposited 950 ETH worth.
7. The Chainlink feed updates; `updateRSETHPrice()` is called; `_getTotalEthInProtocol()` now reflects the true lower stETH price.
8. `rsETHPrice` drops, and the attacker's rsETH is now backed by more ETH per token than other holders' rsETH — the attacker can redeem at a profit, with the loss distributed across all existing rsETH holders. [1](#0-0) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
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
