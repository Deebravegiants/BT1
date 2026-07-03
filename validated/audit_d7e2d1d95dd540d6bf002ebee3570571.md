### Title
Missing Chainlink Response Validation in `ChainlinkPriceOracle.getAssetPrice()` Allows Zero/Stale Price to Silently Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but performs **no validation** on the returned price — no zero/negative check, no stale-round check, no incomplete-round check. A zero price silently passes through, causing `mulWad(assetER)` to zero-out an asset's entire TVL contribution inside `_getTotalEthInProtocol()`, which then corrupts `rsETHPrice`. This is the direct analog to the external report's pattern: a corrupted oracle value passes all downstream "validity" checks and silently distorts the protocol's core pricing invariant.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads only the `price` field from `latestRoundData()` and discards every safety field:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 52-54
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

No check is made that:
- `price > 0` — a zero or negative answer is silently cast and returned
- `answeredInRound >= roundId` — stale-round detection absent
- `updatedAt != 0` — incomplete-round detection absent

The protocol's own `ChainlinkOracleForRSETHPoolCollateral` contract, used for L2 pool collateral, performs all three checks and reverts on failure:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The unvalidated price from `ChainlinkPriceOracle` feeds directly into `LRTOracle._getTotalEthInProtocol()`:

```solidity
uint256 assetER = getAssetPrice(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

If `assetER == 0` (Chainlink returns `price = 0`), `mulWad(0) = 0`, so the entire balance of that asset is silently erased from TVL — the exact analog to the external report's "division result equals 0" pattern. The corrupted `totalETHInProtocol` then propagates into the rsETH price computation:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

This corrupted `rsETHPrice` is then consumed by `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

An artificially low `rsETHPrice` denominator inflates `rsethAmountToMint`, allowing a depositor to receive more rsETH than the assets they contributed are worth.

`updateRSETHPrice()` is a public, permissionless function callable by any address:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [6](#0-5) 

---

### Impact Explanation

**Path A — `pricePercentageLimit > 0` (expected production config):**
The downside protection logic pauses `LRTDepositPool` and `LRTWithdrawalManager` when `newRsETHPrice` drops beyond the configured threshold. [7](#0-6) 
This is a **temporary freezing of funds** (Medium) triggered by a corrupted oracle value that passed no validation gate.

**Path B — `pricePercentageLimit == 0` (limit not yet configured, or drop within limit):**
The corrupted price is written to `rsETHPrice` without any revert. Any depositor who calls `depositAsset()` before the price is corrected receives an inflated rsETH mint amount — **direct theft of protocol funds** (Critical).

---

### Likelihood Explanation

Chainlink feeds can return `price = 0` or a stale answer during:
- L2 sequencer downtime (the feed is not updated but the contract does not check `updatedAt`)
- A feed deprecation or misconfiguration
- A circuit-breaker event where the answer is clamped to the feed's `minAnswer` (which can be 0 for some feeds)

`updateRSETHPrice()` is public; an attacker watching the mempool can race to call it the moment a bad Chainlink round is observed, before any keeper corrects it. No privileged role is required.

---

### Recommendation

Apply the same three guards already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0)            revert IncompleteRound();
if (price <= 0)                revert InvalidPrice();
// optional: add a heartbeat staleness window
// if (block.timestamp - updatedAt > HEARTBEAT) revert StalePrice();
``` [1](#0-0) 

---

### Proof of Concept

1. Chainlink's stETH/ETH feed enters a bad round and returns `price = 0`.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → returns `0`.
4. `totalAssetAmt.mulWad(0) == 0` — stETH's entire balance (say 50 % of TVL) is zeroed out.
5. `newRsETHPrice = (0.5 × correctTVL) / rsethSupply` — half the correct price.
6. If `pricePercentageLimit == 0`: `rsETHPrice` is written as `~0.5 × 1e18`.
7. Attacker calls `depositAsset(stETH, X)` → `rsethAmountToMint = X * getAssetPrice(stETH) / rsETHPrice ≈ 2X` worth of rsETH minted.
8. Attacker redeems the excess rsETH after the oracle recovers, extracting value from existing holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
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
