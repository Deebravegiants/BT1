### Title
No Staleness Validation on Chainlink `latestRoundData()` Enables Stale-Price Minting Abuse - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every return value except `answer`. There is no check on `updatedAt`, `answeredInRound`, or price sign/zero. If a Chainlink feed goes stale (sequencer downtime, feed deprecation, network congestion), the last reported price is silently accepted and used to compute how many rsETH tokens to mint for a depositor. Because `rsETHPrice` is a stored value updated separately, a timing gap between the stale feed and the next price update allows an attacker to mint rsETH at a favourable (incorrect) rate, extracting value from existing holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads the Chainlink aggregator as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

`latestRoundData()` returns five values: `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The code captures only `answer` and ignores:

- `updatedAt` — the timestamp of the last price update (staleness detection)
- `answeredInRound` vs `roundId` — whether the answer belongs to the current round
- sign/zero of `price` — a negative or zero answer would silently corrupt the price

This price is consumed by `LRTOracle._getTotalEthInProtocol()`:

```solidity
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [2](#0-1) 

And directly by `LRTDepositPool.getRsETHAmountToMint()`, which determines how many rsETH tokens a depositor receives:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`rsETHPrice` is a **stored** value updated by a separate call to `updateRSETHPrice()`. [4](#0-3)  This creates a timing gap: if a Chainlink feed becomes stale after the last `rsETHPrice` update, the numerator (`getAssetPrice(asset)`) reflects the stale price while the denominator (`rsETHPrice`) still reflects the correct historical price, causing the minting ratio to be wrong.

---

### Impact Explanation

**Impact: Critical — Direct theft of user funds (existing rsETH holders).**

If a supported LST's Chainlink feed goes stale at a price higher than the true market price, an attacker deposits that LST and receives more rsETH than the deposited collateral is actually worth. The excess rsETH represents a dilution of all existing holders' claims on the underlying TVL. The attacker can then sell or redeem the rsETH, extracting real ETH value from the pool at the expense of honest holders.

The same stale price also flows into `_updateRsETHPrice()` via `_getTotalEthInProtocol()`, inflating the computed TVL and potentially triggering the `PriceAboveDailyThreshold` guard — but only if `updateRSETHPrice()` is called *after* the stale price is already in use for minting, meaning the guard does not prevent the minting abuse in the window between the feed going stale and the next price update.

---

### Likelihood Explanation

Chainlink feeds can become stale in several realistic scenarios:

1. **L2 sequencer downtime** — On Optimism, Arbitrum, or Base, if the sequencer goes offline, Chainlink feeds stop updating. The protocol has L2 pool contracts (`RSETHPoolV2`, `RSETHPoolV3`, etc.) that ultimately rely on the same oracle infrastructure. [5](#0-4) 
2. **Feed deprecation or migration** — Chainlink occasionally deprecates feeds; the last reported price remains readable indefinitely.
3. **Network congestion** — Heartbeat-triggered updates can be delayed during high gas periods.

No special privileges are required. Any user can call `depositAsset()` or `depositETH()` during the staleness window. [6](#0-5) 

---

### Recommendation

Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound)
    = priceFeed.latestRoundData();

require(price > 0, "Invalid price");
require(answeredInRound >= roundId, "Stale round");
require(updatedAt != 0, "Round not complete");
require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");

return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

A per-feed configurable `STALENESS_THRESHOLD` (e.g., heartbeat + buffer) should be stored alongside each feed address. For L2 deployments, additionally integrate a Chainlink L2 Sequencer Uptime Feed check before consuming any price data.

---

### Proof of Concept

1. Assume `cbETH/ETH` Chainlink feed last reported `1.05 ETH` per cbETH and then goes stale (sequencer downtime). True market price drops to `0.95 ETH`.
2. `rsETHPrice` was last updated at `1.05` and has not been refreshed.
3. Attacker calls `depositAsset(cbETH, 100e18, 0, "")`.
4. `getRsETHAmountToMint` computes: `(100e18 * 1.05e18) / rsETHPrice`. Since `rsETHPrice` was computed when cbETH was also `1.05`, the ratio is approximately `100 rsETH` — but the deposited cbETH is only worth `95 ETH` at true market price.
5. Attacker receives `~100 rsETH` backed by only `95 ETH` of real value, diluting all existing holders by `~5 ETH`.
6. Attacker repeats until the daily deposit limit is exhausted or the oracle is corrected. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
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

**File:** contracts/pools/RSETHPoolV2.sol (L26-30)
```text
contract RSETHPoolV2 is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    IERC20WrsETH public wrsETH;
    uint256 public feeBps; // Basis points for fees
    uint256 public feeEarnedInETH;
    address public rsETHOracle;
```
