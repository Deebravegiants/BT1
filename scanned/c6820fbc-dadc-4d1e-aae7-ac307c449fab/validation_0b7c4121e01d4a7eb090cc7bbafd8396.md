### Title
Missing Staleness and Validity Checks in `ChainlinkPriceOracle::getAssetPrice` Silently Returns Zero, Corrupting rsETH Price and Enabling Fund Loss - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but performs no staleness check, no round-completeness check, and no non-zero price validation. If Chainlink returns a stale or zero price, the function silently returns `0`. This zero propagates into `LRTOracle._getTotalEthInProtocol()`, artificially collapsing the computed total ETH in the protocol, which in turn drives `rsETHPrice` to an artificially low value. Any caller of the public `updateRSETHPrice()` can trigger this. The consequences are: (1) if `pricePercentageLimit` is configured, the protocol auto-pauses, temporarily freezing all deposits and withdrawals; (2) if not paused, an attacker can immediately deposit at the deflated rsETH price and receive more rsETH than deserved, diluting all existing holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price with no defensive checks:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();          // updatedAt, answeredInRound discarded
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Three fields returned by `latestRoundData` are silently discarded:
- `updatedAt` — not compared against `block.timestamp` to detect staleness
- `answeredInRound` — not compared against `roundId` to detect an incomplete round
- `price` — not checked to be `> 0`

If any of these conditions is violated, the function returns `0` (or, for a negative `price`, wraps to a huge `uint256`).

This zero flows directly into `LRTOracle._getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol
uint256 assetER = getAssetPrice(asset);          // returns 0 on stale oracle
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);  // contributes 0 for this asset
```

And then into `_updateRsETHPrice()`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

With one asset's ETH value zeroed out, `newRsETHPrice` drops sharply. The downside-protection logic then evaluates:

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

The same zero also corrupts the deposit minting calculation:

```solidity
// contracts/LRTDepositPool.sol
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
// → (amount * 0) / rsETHPrice = 0
```

A user depositing with `minRSETHAmountExpected = 0` would transfer their LST tokens in and receive 0 rsETH.

---

### Impact Explanation

**Scenario A — Protocol Pause (Temporary Freeze of Funds, Medium):**  
`updateRSETHPrice()` is a public, permissionless function. Any external caller can invoke it while a Chainlink feed is stale. If `pricePercentageLimit` is set (which it is in production), the artificial price drop triggers an automatic pause of `LRTDepositPool` and `LRTWithdrawalManager`, freezing all user deposits and withdrawals until an admin manually unpauses.

**Scenario B — Yield Theft via Deflated rsETH Price (High):**  
If `pricePercentageLimit` is not set or the drop is within the limit, `rsETHPrice` is written at the artificially low value. An attacker who calls `updateRSETHPrice()` and then immediately calls `depositAsset()` receives more rsETH per unit of LST than the true exchange rate warrants, diluting all existing rsETH holders' share of the underlying assets.

**Scenario C — User Fund Loss on Deposit (Critical):**  
A user depositing a Chainlink-priced LST with `minRSETHAmountExpected = 0` while the oracle is stale will have their tokens transferred in and receive 0 rsETH in return.

---

### Likelihood Explanation

Chainlink feeds experience staleness during network congestion, sequencer downtime (on L2), or during the heartbeat interval. The `updateRSETHPrice()` function is public and callable by anyone, including bots or adversaries who monitor oracle health. The absence of any staleness guard means the window of exploitability equals the full duration of any oracle outage. This is a realistic, externally-triggerable condition requiring no privileged access.

---

### Recommendation

Add staleness, round-completeness, and positivity checks to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
uint48 constant STALENESS_THRESHOLD = 1 hours; // tune per feed heartbeat

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, `updateRSETHPrice()` should revert (rather than silently proceeding with a zero asset price) if any oracle call fails, to prevent corrupted price updates from being committed to state.

---

### Proof of Concept

1. Chainlink's stETH/ETH feed goes stale (heartbeat missed, e.g., during network congestion).
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle` calls `latestRoundData()` → returns stale `price = 0` → returns `0`.
4. stETH's contribution to `totalETHInProtocol` is zeroed out. Suppose stETH represents 40% of TVL; `totalETHInProtocol` drops by 40%.
5. `newRsETHPrice = (0.6 * previousTVL) / rsethSupply` — a 40% drop.
6. If `pricePercentageLimit` is, say, 5% (`5e16`): `diff > 0.05 * highestRsethPrice` → true → `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` are called.
7. All user deposits and withdrawals are frozen until admin intervention.

**Alternatively (Scenario B):** If `pricePercentageLimit` is 0 or the drop is within limit, `rsETHPrice` is written at the deflated value. Attacker immediately calls `depositAsset(stETH, largeAmount, 0, "")` and receives rsETH at the deflated price, then waits for the oracle to recover and `rsETHPrice` to normalize — extracting value from all existing holders.

---

**Root cause references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L250-282)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
        }

        // downside protection — pause if price drops too far
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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
