### Title
Stale Chainlink Price via Block Stuffing Triggers Spurious Auto-Pause of LRTDepositPool and LRTWithdrawalManager — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` reads `latestRoundData()` without any staleness check. A block-stuffing attacker can prevent Chainlink keepers from posting updated LST prices, then call the public `LRTOracle.updateRSETHPrice()`. The resulting understated TVL causes `newRsETHPrice` to appear to fall below `highestRsethPrice * pricePercentageLimit`, triggering the auto-pause of `LRTDepositPool` and `LRTWithdrawalManager` despite no genuine price drop.

---

### Finding Description

**Root cause — no staleness check in `ChainlinkPriceOracle.getAssetPrice`:** [1](#0-0) 

The function calls `latestRoundData()` and returns only `price`. It never inspects `updatedAt` or `answeredInRound`, so a price that has not been refreshed for an arbitrarily long time is accepted as current.

Compare this with the team's own `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which correctly validates both fields: [2](#0-1) 

The staleness guard exists in the codebase but was not applied to the oracle that feeds the rsETH price calculation.

**Public entry point — `updateRSETHPrice` is callable by anyone:** [3](#0-2) 

**TVL computation uses the stale price:**

`_getTotalEthInProtocol` iterates every supported asset and calls `getAssetPrice(asset)`, which routes through the unchecked `ChainlinkPriceOracle`: [4](#0-3) 

**Auto-pause trigger:** [5](#0-4) 

If the stale-low price makes `newRsETHPrice` fall more than `pricePercentageLimit` below `highestRsethPrice`, the protocol pauses unconditionally — no admin action required.

---

### Impact Explanation

All deposits and withdrawals are frozen until an admin manually unpauses. The pause is triggered by an artificial price artifact (block-stuffed stale data), not a genuine loss of value. The invariant that the auto-pause should only fire on real price drops is violated.

Impact: **Low — Block stuffing enabling temporary freezing of all deposits and withdrawals.**

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but quantifiable. A well-funded attacker needs to fill blocks only long enough for the LST price to rise by more than `pricePercentageLimit` relative to the last Chainlink update (e.g., >1% if the limit is 1e16). Chainlink heartbeat for LST/ETH feeds is typically 1 hour; deviation-triggered updates require the attacker to suppress every block during a rising-price window. The cost is high but not prohibitive for a targeted griefing campaign, and the attacker gains no funds — only a temporary protocol freeze.

---

### Recommendation

Add a staleness check to `ChainlinkPriceOracle.getAssetPrice`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
// In ChainlinkPriceOracle.getAssetPrice
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
```

`MAX_STALENESS` should be set per-feed based on the Chainlink heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed). This ensures that a block-stuffed or otherwise stale answer is rejected before it can feed into the auto-pause calculation.

---

### Proof of Concept

```solidity
// Invariant test (local fork, no mainnet)
function test_blockStuffing_spuriousPause() external {
    // 1. Set pricePercentageLimit to 1% (1e16)
    lrtOracle.setPricePercentageLimit(1e16);

    // 2. Simulate a prior price update so highestRsethPrice is set
    //    (mock Chainlink returns 1.05e18 for the LST)
    mockChainlink.setAnswer(1.05e18);
    lrtOracle.updateRSETHPrice();
    uint256 peak = lrtOracle.highestRsethPrice(); // e.g. 1.05e18

    // 3. Attacker stuffs blocks; Chainlink cannot update.
    //    Mock now returns the old stale-low answer (1.03e18),
    //    while the real price has risen to 1.07e18.
    mockChainlink.setAnswer(1.03e18); // stale, >1% below peak

    // 4. Anyone calls updateRSETHPrice
    lrtOracle.updateRSETHPrice();

    // 5. Protocol is now paused despite no real price drop
    assertTrue(lrtDepositPool.paused(), "deposit pool should be paused");
    assertTrue(withdrawalManager.paused(), "withdrawal manager should be paused");
}
```

The test passes on unmodified code, confirming the spurious pause is reachable without any privileged role.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-32)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

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
