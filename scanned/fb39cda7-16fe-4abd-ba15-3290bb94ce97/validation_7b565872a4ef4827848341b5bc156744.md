### Title
Missing Chainlink Price Feed Staleness Check Allows Stale Prices to Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards the `updatedAt` and `answeredInRound` return values, performing zero staleness validation. A stale price is then propagated through `LRTOracle._getTotalEthInProtocol()` into `_updateRsETHPrice()`, corrupting the rsETH/ETH exchange rate used to mint rsETH for depositors.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` (the price) is read; `updatedAt` (the timestamp of the last oracle update) and `answeredInRound` (the round in which the answer was computed) are both discarded. There is no check of the form `block.timestamp - updatedAt > heartbeat` and no check that `answeredInRound >= roundId`.

This price flows directly into `LRTOracle.getAssetPrice()`:

```solidity
return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
``` [2](#0-1) 

Which is consumed by `_getTotalEthInProtocol()` for every supported LST asset:

```solidity
uint256 assetER = getAssetPrice(asset);
``` [3](#0-2) 

And `_getTotalEthInProtocol()` feeds `_updateRsETHPrice()`, which computes and stores the canonical rsETH price:

```solidity
uint256 totalETHInProtocol = _getTotalEthInProtocol();
...
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

`updateRSETHPrice()` is a public, permissionless function:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

The stored `rsETHPrice` is then used by `LRTDepositPool` to determine how many rsETH tokens to mint per deposit. [6](#0-5) 

By contrast, `ChainlinkOracleForRSETHPoolCollateral` — used in the pool path — does perform partial staleness checks (`answeredInRound < roundID`, `timestamp == 0`), but still omits the time-based heartbeat check. `ChainlinkPriceOracle` performs **no checks at all**. [7](#0-6) 

### Impact Explanation

If a Chainlink feed goes stale (e.g., during network congestion, a sequencer outage on L2, or an oracle node failure), `latestRoundData()` continues to return the last recorded price without reverting. Because `updatedAt` is never checked, this stale price is accepted as current. A stale price that is **artificially low** causes `_updateRsETHPrice()` to compute a deflated rsETH price, allowing a depositor to mint more rsETH than the deposited assets are worth — directly diluting and stealing value from existing rsETH holders. A stale price that is **artificially high** causes depositors to receive fewer rsETH tokens than they are entitled to. Either direction constitutes incorrect fund accounting. The impact is **theft of unclaimed yield / incorrect fund distribution** (High) in the low-price-stale scenario, and **contract fails to deliver promised returns** (Low) in the high-price-stale scenario.

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for ETH/USD on mainnet, 24 hours for some LST feeds). During periods of low volatility, feeds may not update for the full heartbeat window. Any depositor who calls `updateRSETHPrice()` followed by `depositAsset()` during a stale window can exploit the mispricing. No special privileges are required; the entry path is fully permissionless.

### Recommendation

Add a configurable staleness threshold and validate both `updatedAt` and `answeredInRound` in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (block.timestamp - updatedAt > stalenessThreshold) revert StalePrice();
if (price <= 0) revert InvalidPrice();
```

### Proof of Concept

1. A Chainlink LST/ETH feed used by `ChainlinkPriceOracle` goes stale (last update was 2 hours ago; heartbeat is 1 hour). The feed still returns the old, lower price.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (permissionless). `_getTotalEthInProtocol()` reads the stale low price for the LST, computing a deflated total ETH value. `newRsETHPrice` is set below its true value and stored.
3. Attacker immediately calls `LRTDepositPool.depositAsset()` with the LST. The deposit pool uses the now-deflated `rsETHPrice` to compute `rsethAmountToMint`, minting more rsETH than the deposited assets are worth.
4. When the oracle recovers and `rsETHPrice` is corrected upward, the attacker's excess rsETH represents a claim on more underlying assets than they deposited, at the expense of existing holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTOracle.sol (L339-339)
```text
            uint256 assetER = getAssetPrice(asset);
```

**File:** contracts/LRTDepositPool.sol (L87-91)
```text
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

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
