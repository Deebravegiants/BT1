### Title
Stale Chainlink Price Accepted Without Timestamp Validation Enables Oracle Rate Abuse - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards every staleness indicator (`updatedAt`, `answeredInRound`). The returned price is fed directly into rsETH mint-amount and rsETH/ETH rate calculations with no heartbeat or round-completeness guard.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` destructures the Chainlink response as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
``` [1](#0-0) 

`updatedAt` (position 4) and `answeredInRound` (position 5) are both discarded. No check of the form `block.timestamp - updatedAt > heartbeat` or `answeredInRound < roundId` is performed. A price that is hours or days old is accepted as current.

This stale price propagates through two critical paths:

**Path 1 — rsETH mint amount (deposit flow)**
`LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)`, which delegates to `ChainlinkPriceOracle.getAssetPrice()`.

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

**Path 2 — rsETH/ETH rate update**
`LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported LST to compute total protocol TVL, which then sets `rsETHPrice`.

```solidity
uint256 assetER = getAssetPrice(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

Note: `ChainlinkOracleForRSETHPoolCollateral` checks `answeredInRound < roundID` but still omits the time-based `block.timestamp - timestamp > maxDelay` guard, leaving it partially vulnerable as well. [5](#0-4) 

### Impact Explanation
**High — Theft of unclaimed yield from existing rsETH holders.**

If a supported LST's Chainlink feed goes stale at a price *below* the true market price (e.g., during network congestion after a positive rebase), `_getTotalEthInProtocol()` understates TVL. `updateRSETHPrice()` then sets `rsETHPrice` lower than it should be. A depositor calling `depositAsset` immediately after receives *more* rsETH per unit of LST than the true exchange rate warrants, diluting the share value of all existing holders and transferring their accrued yield to the new depositor.

The reverse (stale price above true price) causes the depositor to receive fewer rsETH, but the primary theft vector is the underpriced-oracle scenario.

### Likelihood Explanation
Chainlink feeds have documented heartbeat intervals (e.g., 24 h for stETH/ETH on mainnet) and can lag during L2 sequencer downtime or extreme network congestion. The absence of any staleness check means the full heartbeat window — potentially 24 hours of price drift — is exploitable. Any unprivileged depositor can trigger `depositAsset` or call `updateRSETHPrice` (public, permissionless) at any time. [6](#0-5) 

### Recommendation
Add a configurable `maxStaleness` per feed and revert if the price is too old:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= maxStaleness[asset], "Stale price");
```

Apply the same time-based guard to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

### Proof of Concept
1. Chainlink stETH/ETH feed last updated at `T - 20h`; true stETH price has risen 0.5% since then.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public). `_getTotalEthInProtocol()` uses the stale (low) stETH price → `rsETHPrice` is set ~0.5% below true value.
3. Attacker immediately calls `LRTDepositPool.depositAsset(stETH, largeAmount, 0)`. `getRsETHAmountToMint` divides by the depressed `rsETHPrice`, minting ~0.5% excess rsETH.
4. Attacker holds or redeems the excess rsETH once the oracle updates, extracting value from existing holders.

No privileged access is required; both `updateRSETHPrice` and `depositAsset` are reachable by any external caller. [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTOracle.sol (L87-88)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```
