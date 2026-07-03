### Title
Unchecked `int256`→`uint256` Cast of Chainlink Price Silently Accepts Non-Positive Values — (`File: contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the raw `int256 answer` from Chainlink's `latestRoundData()` directly to `uint256` with no sign check. If Chainlink returns `price ≤ 0` (circuit-breaker, sequencer outage, or stale feed), the cast either wraps to a near-`type(uint256).max` value (negative input → arithmetic overflow revert, DoS) or silently returns `0` (zero input → zero asset price propagated into rsETH price calculation). Both paths corrupt the protocol's accounting and freeze user funds. The sister oracle `ChainlinkOracleForRSETHPoolCollateral` in the same repo already applies the correct guard (`if (ethPrice <= 0) revert InvalidPrice()`), confirming the fix is known and the omission in `ChainlinkPriceOracle` is an oversight.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads the Chainlink answer as `int256` and immediately casts it to `uint256`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no guard of the form `require(price > 0)`. Chainlink's specification explicitly allows `answer` to be zero or negative (e.g., when a price feed hits its minimum circuit-breaker value). Two failure modes follow:

**Case A — `price < 0`:** `uint256(negative_int256)` produces a value near `2^256`. The subsequent `* 1e18` multiplication overflows and reverts under Solidity 0.8's checked arithmetic. Every call that routes through this oracle reverts.

**Case B — `price == 0`:** `uint256(0) * 1e18 / decimals = 0`. The function returns `0` silently. This zero propagates into `LRTOracle._updateRsETHPrice()` as the asset's ETH value, collapsing `totalETHInProtocol` and driving `newRsETHPrice` toward zero.

The correct pattern is already present in the same codebase:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle registered for LST assets (stETH, etc.) in `LRTOracle` via `assetPriceOracle`: [3](#0-2) 

---

### Impact Explanation

**Case A (negative price → overflow revert):**

The revert propagates through the full deposit call stack:

`depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()` → overflow revert. [4](#0-3) 

All LST deposits are frozen for the duration of the anomalous Chainlink round. `updateRSETHPrice()` also reverts, preventing price updates and blocking the withdrawal manager's price-dependent logic.

**Case B (zero price → silent zero):**

`_updateRsETHPrice()` computes `totalETHInProtocol` using the zero asset price, producing a drastically lower `newRsETHPrice`. The downside-protection logic then pauses `LRTDepositPool` and `LRTWithdrawalManager`:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [5](#0-4) 

This is a **temporary freezing of funds** (Medium impact). Deposits and withdrawals are halted until an admin manually unpauses after the oracle recovers.

---

### Likelihood Explanation

Chainlink feeds for LST/ETH pairs (stETH/ETH) are mature and rarely return non-positive values under normal conditions. However:

- Chainlink circuit breakers clamp prices at configured min/max values; a feed can return `0` if misconfigured or during extreme market stress.
- Any public caller of `updateRSETHPrice()` (permissionless) triggers the path; no privileged role is required.
- The same codebase already defends against this in `ChainlinkOracleForRSETHPoolCollateral`, indicating the team is aware of the risk for other oracle wrappers.

Likelihood: **Low** (requires an anomalous Chainlink round), but the impact when triggered is a full protocol pause.

---

### Recommendation

Add a non-positive price guard in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();  // <-- add this

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding staleness checks (`updatedAt`, `answeredInRound`) consistent with `ChainlinkOracleForRSETHPoolCollateral`.

---

### Proof of Concept

1. Chainlink's stETH/ETH feed enters a circuit-breaker state and returns `answer = 0` for one round.
2. Any caller (e.g., a keeper bot or a user) calls `LRTOracle.updateRSETHPrice()`.
3. `_updateRsETHPrice()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns `0`.
4. `_getTotalEthInProtocol()` sums asset values; stETH contributes `0 * balance / 1e18 = 0`, collapsing TVL.
5. `newRsETHPrice` drops far below `highestRsethPrice`; `isPriceDecreaseOffLimit` is `true`.
6. `LRTDepositPool.pause()` and `LRTWithdrawalManager.pause()` are called automatically.
7. All user deposits and withdrawals are frozen until an admin unpauses — a temporary freeze of funds. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L32-32)
```text
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
