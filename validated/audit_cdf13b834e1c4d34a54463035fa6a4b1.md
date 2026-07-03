### Title
Missing L2 Sequencer Uptime Check and Staleness Validation in Chainlink Oracle Allows Stale Price Usage on Arbitrum - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` with **zero validation** — no staleness check, no round completeness check, no price validity check, and critically no L2 sequencer uptime check. The protocol is deployed on Arbitrum. During or immediately after an Arbitrum sequencer outage, stale Chainlink prices are silently accepted and used to compute the rsETH exchange rate, causing incorrect rsETH minting for depositors.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price with no guards whatsoever: [1](#0-0) 

The raw `latestRoundData()` return value is used directly — `roundId`, `updatedAt`, and `answeredInRound` are all discarded. There is no check that:
- `answeredInRound >= roundId` (round completeness)
- `updatedAt` is recent (staleness)
- `price > 0` (validity)
- The Arbitrum sequencer is live (L2 sequencer uptime)

This price feeds directly into `LRTOracle._getTotalEthInProtocol()`, which sums the ETH value of all supported LST assets: [2](#0-1) 

That total is then used in `_updateRsETHPrice()` to compute and store the new `rsETHPrice`: [3](#0-2) 

`updateRSETHPrice()` is a public, permissionless function callable by anyone: [4](#0-3) 

A secondary instance exists in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which does perform basic round/timestamp/sign checks but still omits the sequencer uptime check: [5](#0-4) 

No sequencer uptime feed is referenced anywhere in the production contract set — confirmed by a full-codebase grep for `sequencer`, `sequencerUptimeFeed`, and `GRACE_PERIOD`.

---

### Impact Explanation

When the Arbitrum sequencer goes offline, Chainlink oracle updates stop. When the sequencer restarts, there is a window (Chainlink recommends a 1-hour grace period) during which the reported prices are stale. Because `updateRSETHPrice()` is public and permissionless, any external caller — including a depositor acting in self-interest — can invoke it during this window.

- If stale prices are **inflated** relative to true market prices (e.g., a crash occurred during the outage), `rsETHPrice` is computed too high. New depositors receive fewer rsETH tokens than they are entitled to. Existing holders are not harmed, but new depositors suffer a loss relative to fair value.
- If stale prices are **deflated** (e.g., a rally occurred during the outage), `rsETHPrice` is computed too low. New depositors receive more rsETH than they should, diluting existing holders.
- In either case, the price deviation may be large enough to trigger the downside protection pause in `_updateRsETHPrice()`, temporarily freezing deposits and withdrawals for all users.

**Impact: Low — Contract fails to deliver promised returns (incorrect rsETH minting amounts). Escalates to Medium (temporary fund freeze) if the stale price deviation exceeds `pricePercentageLimit`.**

---

### Likelihood Explanation

Arbitrum has experienced sequencer outages historically. The protocol is confirmed deployed on Arbitrum per the README. `updateRSETHPrice()` is public and requires no privilege. Any user can trigger the stale-price update immediately after the sequencer restarts, before Chainlink has published fresh data. The attack requires no capital, no special access, and no coordination — only timing awareness.

---

### Recommendation

Add a sequencer uptime check using Chainlink's L2 Sequencer Uptime Feed before consuming any price data in `ChainlinkPriceOracle.getAssetPrice()`. Also add the missing staleness and validity guards:

```solidity
// In ChainlinkPriceOracle (or a shared library):
uint256 constant GRACE_PERIOD_TIME = 3600; // 1 hour

function _checkSequencer() internal view {
    (, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
    // answer == 0: sequencer is up; answer == 1: sequencer is down
    if (answer == 1 || block.timestamp - startedAt < GRACE_PERIOD_TIME) {
        revert SequencerDown();
    }
}

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    _checkSequencer(); // add this
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Apply the same sequencer check to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

Reference: https://docs.chain.link/data-feeds/l2-sequencer-feeds

---

### Proof of Concept

1. Protocol is live on Arbitrum (README confirmed, `ChainlinkPriceOracle` deployed at `0x78C12ccE8346B936117655Dd3D70a2501Fd3d6e6`).
2. Arbitrum sequencer goes offline. Chainlink stops updating LST/ETH price feeds.
3. During the outage, the true market price of a supported LST (e.g., stETH) drops 5%.
4. Sequencer restarts. Chainlink feed still reports the pre-outage (inflated) price.
5. Attacker (or any user) calls `LRTOracle.updateRSETHPrice()` immediately.
6. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice()` → `latestRoundData()` returns the stale inflated price with no revert.
7. `rsETHPrice` is set ~5% above true value.
8. A depositor calling `LRTDepositPool.depositAsset()` receives ~5% fewer rsETH tokens than the fair amount, since rsETH is priced too high relative to the deposited asset's true value.
9. No admin action, no special role, no capital required — only a public function call at the right moment. [1](#0-0) [4](#0-3) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
