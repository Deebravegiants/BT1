### Title
Stale Chainlink Price Accepted Without Any Staleness Validation Enables Incorrect rsETH Minting and Withdrawal Amounts - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards every validity field — `updatedAt`, `answeredInRound`, and `roundId` — accepting whatever price the feed last stored with no temporal check. This stale price propagates directly into rsETH mint calculations and withdrawal amount calculations, allowing a depositor to receive more rsETH than the protocol's actual TVL supports when a feed is stale at an inflated value.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` destructures `latestRoundData()` retaining only `price`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
``` [1](#0-0) 

None of the following checks are present:
- `answeredInRound >= roundId` — detects a round that was never completed
- `updatedAt != 0` — detects an incomplete round
- `block.timestamp - updatedAt <= MAX_STALENESS` — detects a price that has not been refreshed within an acceptable window
- `price > 0` — detects a zero/negative answer

By contrast, the sister contract `ChainlinkOracleForRSETHPoolCollateral` used in the L2 pool system does perform the first two checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

Even that contract omits a maximum-age check, but `ChainlinkPriceOracle` omits all three.

The stale price propagates through the following call chain:

1. `LRTOracle.getAssetPrice(asset)` delegates to `IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset)`, which resolves to `ChainlinkPriceOracle`. [3](#0-2) 

2. `LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported LST and multiplies by total deposits to compute the protocol's ETH-denominated TVL. [4](#0-3) 

3. `LRTOracle._updateRsETHPrice()` derives `newRsETHPrice` from that TVL figure. [5](#0-4) 

4. `LRTDepositPool.getRsETHAmountToMint()` uses both `lrtOracle.getAssetPrice(asset)` (stale) and `lrtOracle.rsETHPrice()` (last stored, potentially correct) to determine how many rsETH tokens to mint per deposited LST. [6](#0-5) 

5. `LRTWithdrawalManager.getExpectedAssetAmount()` uses `lrtOracle.getAssetPrice(asset)` to determine how many LST tokens a withdrawer receives per rsETH burned. [7](#0-6) 

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield / dilution of existing rsETH holders.**

When a Chainlink LST/ETH feed goes stale at a price higher than the actual market price (e.g., stETH was 1.05 ETH but has since dropped to 0.99 ETH due to a slashing event or market move, while the feed has not yet updated), the following occurs:

- `getAssetPrice(stETH)` returns the stale 1.05 ETH value.
- `_getTotalEthInProtocol()` overcounts the protocol's TVL.
- `getRsETHAmountToMint(stETH, amount)` = `amount × 1.05 / rsETHPrice` — the depositor receives more rsETH than the actual ETH value of their deposit warrants.
- The inflated rsETH balance dilutes all existing rsETH holders, effectively transferring yield from them to the attacker.

The inverse (stale price below actual) causes withdrawers to receive fewer assets than they are owed, constituting a temporary freeze of the difference.

---

### Likelihood Explanation

Chainlink LST/ETH feeds (e.g., stETH/ETH) have heartbeat intervals of up to 24 hours. During network congestion, oracle node failures, or feed deprecation, the feed can remain stale for the entire heartbeat window without any on-chain revert. An attacker monitoring mempool and Chainlink feed timestamps can detect the staleness condition and act within the same block. No privileged access is required — `depositAsset()` is callable by any user.

---

### Recommendation

Apply the same pattern already used in `ChainlinkOracleForRSETHPoolCollateral`, extended with a maximum-age bound, inside `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (price <= 0) revert InvalidPrice();
if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice(); // e.g. 25 hours
```

`MAX_STALENESS` should be set per-feed based on the feed's documented heartbeat.

---

### Proof of Concept

1. The stETH/ETH Chainlink feed last updated at `T-20h` with price `1.05 ETH`. The actual stETH price has since dropped to `0.99 ETH` due to a slashing event, but the feed has not yet triggered a deviation update.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0)`.
3. `getRsETHAmountToMint(stETH, 100e18)` computes `100e18 × 1.05e18 / rsETHPrice`. With `rsETHPrice = 1.04e18` (last correctly stored), the attacker receives `≈ 100.96 rsETH` instead of the correct `≈ 95.19 rsETH` (based on actual 0.99 ETH price).
4. The attacker holds `≈ 5.77` excess rsETH backed by no real ETH value, diluting all existing holders proportionally.
5. No admin action, no privileged role, and no oracle operator compromise is required — the stale feed is a passive condition that any user can exploit by timing their deposit.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
