### Title
Unvalidated Chainlink `latestRoundData()` Return Values Enable Attacker-Triggered Protocol Pause — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every return value except the raw `int256 price`, performing no staleness, completeness, or sign validation. Because `updateRSETHPrice()` is a public function, any unprivileged caller can invoke it while a Chainlink feed is stale, causing the computed rsETH price to drop artificially and trigger the protocol's automatic downside-protection pause, temporarily freezing all deposits and withdrawals.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate used to value all protocol collateral:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-L55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (, int256 price,,,) = priceFeed.latestRoundData();   // ← roundId, startedAt, updatedAt, answeredInRound all discarded

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

No check is made for:
- `price > 0` — a zero or negative `int256` is silently cast to `uint256` (zero or a huge two's-complement value)
- `answeredInRound >= roundId` — stale round detection
- `updatedAt != 0` — incomplete round detection
- Any heartbeat/freshness window

The same codebase already implements all three checks in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-L32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();

if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The unvalidated price flows through the following call chain:

1. `ChainlinkPriceOracle.getAssetPrice(asset)` → stale/zero price returned
2. `LRTOracle.getAssetPrice(asset)` (line 157) → passes it through
3. `LRTOracle._getTotalEthInProtocol()` (line 339) → underestimates total ETH in protocol
4. `LRTOracle._updateRsETHPrice()` (line 250) → computes artificially low `newRsETHPrice`
5. Lines 270–281: if `newRsETHPrice` drops more than `pricePercentageLimit` below `highestRsethPrice`, the contract calls `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` — freezing all user deposits and withdrawals

The entry point is fully public:

```solidity
// contracts/LRTOracle.sol L87-L89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Any address can call `updateRSETHPrice()` at any time, including during a period when a Chainlink feed is stale.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

If the attack succeeds, `LRTDepositPool` and `LRTWithdrawalManager` are both paused. All user deposits and withdrawals are blocked until an admin with `LRTAdmin` role manually unpauses. No funds are permanently lost, but users cannot access their assets or exit positions for an indeterminate period.

---

### Likelihood Explanation

Chainlink feeds go stale during network congestion or oracle node outages — this is a documented, recurring real-world event. The trigger function `updateRSETHPrice()` is permissionless. An attacker can monitor on-chain feed freshness and call `updateRSETHPrice()` the moment a feed's `answeredInRound < roundId` or `updatedAt` is old, reliably triggering the pause. No privileged access, no front-running, and no capital is required.

---

### Recommendation

Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a configurable heartbeat staleness window (e.g., `block.timestamp - updatedAt > MAX_STALENESS`) per feed.

---

### Proof of Concept

1. A Chainlink LST/ETH feed (e.g., stETH/ETH) enters a stale round: `answeredInRound < roundId`. The last reported price is significantly below the true current price (e.g., due to a delayed update during high gas).

2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control).

3. `_updateRsETHPrice()` calls `_getTotalEthInProtocol()`, which calls `LRTOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns the stale, depressed price without reverting.

4. `totalETHInProtocol` is underestimated. `newRsETHPrice` is computed as lower than `highestRsethPrice` by more than `pricePercentageLimit`.

5. Lines 277–281 execute: `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` — the entire protocol is frozen.

6. All depositors and withdrawers are blocked until an admin manually unpauses. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
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
