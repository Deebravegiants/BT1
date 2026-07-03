Looking at the key contracts:

### Title
Stale `rsETHPrice` silently propagated through `RSETHPriceFeed.latestRoundData` with a misleading `updatedAt` timestamp — (`contracts/oracles/RSETHPriceFeed.sol`)

---

### Summary

`RSETHPriceFeed.latestRoundData` computes a composite rsETH/USD price by multiplying a stored `rsETHPrice` (from `LRTOracle`) by a live ETH/USD Chainlink price. The `updatedAt` field it returns comes exclusively from the ETH/USD Chainlink feed, not from when `rsETHPrice` was last written. If `LRTOracle.updateRSETHPrice()` has not been called for an extended period, the rsETH/ETH component is stale while `updatedAt` still appears fresh to any downstream consumer.

---

### Finding Description

`RSETHPriceFeed.latestRoundData` is implemented as:

```solidity
// contracts/oracles/RSETHPriceFeed.sol lines 63-70
function latestRoundData()
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
``` [1](#0-0) 

`RS_ETH_ORACLE.rsETHPrice()` reads the storage variable `rsETHPrice` from `LRTOracle`:

```solidity
// contracts/LRTOracle.sol line 28
uint256 public override rsETHPrice;
``` [2](#0-1) 

This variable is only written by `_updateRsETHPrice()`, which is called from the public `updateRSETHPrice()` (gated by `whenNotPaused`) or the manager-only `updateRSETHPriceAsManager()`:

```solidity
// contracts/LRTOracle.sol lines 87-96
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
function updateRSETHPriceAsManager() external onlyLRTManager {
    _updateRsETHPrice();
}
``` [3](#0-2) 

And the final write happens at:

```solidity
// contracts/LRTOracle.sol line 313
rsETHPrice = newRsETHPrice;
``` [4](#0-3) 

There is no on-chain enforcement of how frequently `updateRSETHPrice()` must be called, and `RSETHPriceFeed` does not record or expose a timestamp for when `rsETHPrice` was last refreshed. The `updatedAt` value returned by `latestRoundData()` is sourced entirely from the ETH/USD Chainlink feed (line 68), which can be updated independently and frequently. [5](#0-4) 

Additionally, if the protocol is paused (e.g., due to a price deviation triggering `_pause()` at line 280), `updateRSETHPrice()` reverts due to `whenNotPaused`, making it impossible for anyone to refresh `rsETHPrice` through the public path during that window. [6](#0-5) 

---

### Impact Explanation

A downstream lending protocol integrating `RSETHPriceFeed` as a Chainlink-compatible oracle will:
1. Call `latestRoundData()` and receive `updatedAt` from the ETH/USD feed — which may be seconds old.
2. Pass its own staleness check (e.g., `require(block.timestamp - updatedAt < 3600)`).
3. Use the returned `answer` as the rsETH/USD price — which silently embeds a potentially days-old rsETH/ETH rate.

This causes the composite price to diverge from the true rsETH/USD value without any on-chain signal of staleness, leading to incorrect collateral valuations. The contract fails to deliver the promised fresh composite price. No direct fund loss occurs within the LRT-rsETH contracts themselves, matching the **Low** scope: *contract fails to deliver promised returns, but doesn't lose value*. [1](#0-0) 

---

### Likelihood Explanation

- `updateRSETHPrice()` is public and callable by anyone, so under normal operation it can be kept fresh by keepers or bots.
- However, during a protocol pause (triggered automatically by price deviation logic), the public update path is blocked, and only the manager can refresh the price. A pause of meaningful duration (hours to days) is a realistic scenario given the existing pause-on-deviation logic.
- Even outside a pause, there is no on-chain guarantee of update frequency; if keeper infrastructure fails, staleness accumulates silently. [7](#0-6) 

---

### Recommendation

`RSETHPriceFeed` should track and expose the timestamp of the last `rsETHPrice` update. The `updatedAt` field returned by `latestRoundData` and `getRoundData` should be `min(ethToUSD_updatedAt, rsETHPrice_updatedAt)` so downstream consumers see the true staleness of the composite price. Concretely:

1. Add a `uint256 public rsETHPriceUpdatedAt` variable to `LRTOracle` (or expose it via the `IRSETHOracle` interface).
2. Set it to `block.timestamp` inside `_updateRsETHPrice()` alongside `rsETHPrice = newRsETHPrice`.
3. In `RSETHPriceFeed.latestRoundData`, override `updatedAt` with `min(updatedAt, RS_ETH_ORACLE.rsETHPriceUpdatedAt())`. [1](#0-0) 

---

### Proof of Concept

```solidity
// Fork test (local fork, no mainnet)
function test_staleRsETHPrice() public {
    // Warp 48 hours without calling updateRSETHPrice
    vm.warp(block.timestamp + 48 hours);

    (, int256 answer,, uint256 updatedAt,) = rsETHPriceFeed.latestRoundData();

    // updatedAt reflects ETH/USD freshness (recent), not rsETH/ETH freshness (48h stale)
    assertApproxEqAbs(updatedAt, block.timestamp, 3600, "updatedAt appears fresh");

    // But rsETHPrice embedded in answer is 48h old
    uint256 trueRsETHPrice = computeTrueRsETHPrice(); // recompute from current EigenLayer state
    int256 trueAnswer = int256(trueRsETHPrice) * ethUsdPrice / 1e18;

    // answer diverges from trueAnswer by more than acceptable threshold
    assertGt(
        uint256(answer > trueAnswer ? answer - trueAnswer : trueAnswer - answer),
        acceptableThreshold,
        "stale composite price"
    );
}
``` [1](#0-0)

### Citations

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

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L138-140)
```text
    function pause() external whenNotPaused onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
