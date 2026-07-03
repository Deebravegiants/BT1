### Title
Missing L2 Sequencer Uptime Check and Staleness Validation in `ChainlinkPriceOracle` Allows Stale LST Prices on L2 - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` with no L2 sequencer uptime check and no staleness/validity validation. This oracle is used by L2 liquidity pools (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`) to price LST deposits (e.g., wstETH). During an L2 sequencer outage, the frozen stale price can be exploited to mint excess wrsETH/rsETH.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate used by all L2 deposit pools:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Three defects are present simultaneously:
1. **No L2 sequencer uptime check** — Chainlink's L2 sequencer uptime feed is never consulted.
2. **No staleness check** — `updatedAt` is silently discarded (fifth return value ignored).
3. **No validity check** — `answer > 0` is never asserted.

This oracle is wired into every L2 pool's token deposit path. In `RSETHPoolV3` and `RSETHPoolV3ExternalBridge`, the LST-to-wrsETH conversion is:

```solidity
// RSETHPoolV3.sol L331-334 / RSETHPoolV3ExternalBridge.sol L449-452
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`supportedTokenOracle[token]` resolves to a `ChainlinkPriceOracle` instance for LST tokens such as wstETH. The same pattern exists in `RSETHPoolNoWrapper` at line 308.

When the L2 sequencer goes offline, Chainlink stops updating its L2 price feeds. The `latestRoundData()` call returns the last pre-downtime answer with a `updatedAt` timestamp that is now stale, but the contract accepts it unconditionally.

### Impact Explanation
**Impact: Low to Medium — Contract fails to deliver promised returns / Temporary freezing of funds / Theft of unclaimed yield.**

If the LST/ETH price drops during sequencer downtime (e.g., a slashing event, market dislocation), the frozen Chainlink feed still reports the pre-downtime (higher) price. A depositor who submits a transaction immediately after the sequencer resumes — before the oracle updates — receives:

```
rsETHAmount = amountAfterFee * staleHigherTokenRate / rsETHToETHrate
```

This mints more wrsETH than the deposited LST is actually worth, extracting value from the pool at the expense of existing holders. Conversely, if the LST price rose during downtime, honest depositors receive fewer wrsETH than they deserve, causing a loss of promised returns.

### Likelihood Explanation
L2 sequencer outages have occurred historically on Arbitrum and Optimism. The protocol is explicitly deployed on these networks (Arbitrum, Optimism, Base, Linea, Unichain per the pool contracts). LST price movements during outages are realistic (staking reward accrual, slashing). The attack requires no special privilege — any depositor can call `deposit(token, amount, referralId)` immediately after sequencer recovery.

### Recommendation
1. Integrate Chainlink's L2 sequencer uptime feed (per [Chainlink docs](https://docs.chain.link/data-feeds/l2-sequencer-feeds)) into `ChainlinkPriceOracle` or into a shared oracle wrapper used by all L2 pools. Revert if the sequencer is down or within a grace period after recovery.
2. Add staleness validation: `require(block.timestamp - updatedAt < staleThreshold, "Stale price")`.
3. Add validity check: `require(price > 0, "Invalid price")`.

### Proof of Concept
1. Deploy on Arbitrum (or Optimism). wstETH is added as a supported token in `RSETHPoolV3ExternalBridge` with a `ChainlinkPriceOracle` pointing to the wstETH/ETH Chainlink feed.
2. L2 sequencer goes offline. During downtime, wstETH/ETH price drops from 1.15 to 1.10 (slashing event). Chainlink feed is frozen at 1.15.
3. Sequencer resumes. Chainlink feed has not yet updated.
4. Attacker calls `deposit(wstETH, 100e18, "")` on `RSETHPoolV3ExternalBridge`.
5. `viewSwapRsETHAmountAndFee` calls `IOracle(supportedTokenOracle[wstETH]).getRate()` → `ChainlinkPriceOracle.getAssetPrice(wstETH)` → returns stale `1.15e18`.
6. `rsETHAmount = 100e18 * 1.15e18 / rsETHToETHrate` — attacker receives wrsETH valued at 1.15 ETH per wstETH, but deposited wstETH worth only 1.10 ETH each.
7. Attacker redeems wrsETH on L1 for ~4.5% excess ETH, extracting value from the pool. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L329-334)
```text

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L447-452)
```text

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L305-311)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
