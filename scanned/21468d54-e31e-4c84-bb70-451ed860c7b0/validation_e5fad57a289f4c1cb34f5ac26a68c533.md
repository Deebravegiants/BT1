### Title
Chainlink `minAnswer` Circuit Breaker Not Validated in `getAssetPrice()`, Enabling Deposit at Inflated Price - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` without checking the returned answer against the aggregator's `minAnswer`/`maxAnswer` bounds. If a supported LST asset crashes in value and the Chainlink aggregator hits its circuit-breaker floor, the oracle silently returns `minAnswer` instead of the real price. This inflated price propagates into rsETH minting, allowing an attacker to deposit the crashed asset and receive rsETH backed by the full protocol portfolio.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and uses the raw `price` return value with no bounds validation: [1](#0-0) 

Chainlink aggregators enforce a `minAnswer` floor. When an asset's market price falls below this floor (e.g., a de-peg or LUNA-style collapse), the aggregator does not revert — it returns `minAnswer`. The protocol has no mechanism to detect this condition.

This price is consumed by `LRTOracle.getAssetPrice()`: [2](#0-1) 

Which feeds into `_getTotalEthInProtocol()`: [3](#0-2) 

Which is called inside `_updateRsETHPrice()` to compute the new rsETH/ETH exchange rate: [4](#0-3) 

`updateRSETHPrice()` is a public, permissionless function: [5](#0-4) 

The same vulnerability exists in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which checks `ethPrice <= 0` but does not validate against `minAnswer`/`maxAnswer`: [6](#0-5) 

And in `RSETHPriceFeed.latestRoundData()`, which passes through the raw ETH/USD answer without bounds checking: [7](#0-6) 

---

### Impact Explanation

When a supported LST asset (e.g., stETH, rETH) crashes below the Chainlink `minAnswer` floor:

1. `getAssetPrice()` returns `minAnswer` (e.g., 0.5 ETH) instead of the real price (e.g., 0.001 ETH).
2. `_getTotalEthInProtocol()` overestimates total ETH, inflating `rsETHPrice`.
3. An attacker buys the crashed asset cheaply on the open market and deposits it via `LRTDepositPool.depositAsset()`.
4. The deposit is valued at the inflated oracle price, minting rsETH that represents a claim on the full protocol portfolio (including healthy assets).
5. The attacker redeems rsETH for healthy assets, extracting value from honest depositors.

This constitutes direct theft of user funds at rest. **Impact: Critical.**

---

### Likelihood Explanation

Chainlink `minAnswer` circuit breakers are a known, documented behavior. The Venus/LUNA incident on BSC is a real precedent. The LRT-rsETH protocol supports multiple LST assets, each with its own Chainlink feed and its own `minAnswer`. A de-peg event on any single supported asset is sufficient to trigger this path. `updateRSETHPrice()` is permissionless, so the attacker can time the price update to coincide with their deposit. **Likelihood: Medium** (requires an asset crash event, but the attack is fully permissionless once it occurs).

---

### Recommendation

In `ChainlinkPriceOracle.getAssetPrice()`, after calling `latestRoundData()`, retrieve the aggregator's `minAnswer` and `maxAnswer` from the `AggregatorV2V3Interface` and revert if the returned price is at or outside those bounds:

```solidity
// Add to AggregatorV3Interface or use AggregatorV2V3Interface
function minAnswer() external view returns (int192);
function maxAnswer() external view returns (int192);

// In getAssetPrice():
(, int256 price,,,) = priceFeed.latestRoundData();
int192 minAns = IFeedWithBounds(address(priceFeed)).minAnswer();
int192 maxAns = IFeedWithBounds(address(priceFeed)).maxAnswer();
if (price <= minAns || price >= maxAns) revert OracleAtCircuitBreaker();
```

Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()` and `RSETHPriceFeed.latestRoundData()`.

---

### Proof of Concept

1. Assume stETH is a supported asset with a Chainlink feed whose `minAnswer` = 0.5e18 (0.5 ETH).
2. stETH de-pegs catastrophically; real market price = 0.001 ETH.
3. Chainlink aggregator hits circuit breaker; `latestRoundData()` returns `answer = 0.5e18`.
4. Attacker buys 1000 stETH on the open market for ~1 ETH worth of value.
5. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0)`.
6. Protocol values the deposit at `1000 * 0.5 = 500 ETH` via the inflated oracle.
7. rsETH is minted to the attacker representing a 500 ETH claim on the protocol.
8. Attacker calls `LRTWithdrawalManager` to redeem rsETH for rETH or other healthy assets.
9. Attacker extracts ~500 ETH worth of healthy assets having spent ~1 ETH — draining honest depositors. [8](#0-7) [9](#0-8)

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

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-36)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```
