### Title
`RSETHPriceFeed` Returns ETH/USD Staleness Metadata While Embedding a Potentially Stale Cached rsETH Price - (File: contracts/oracles/RSETHPriceFeed.sol)

### Summary

`RSETHPriceFeed` is a Chainlink-compatible price feed (deployed on mainnet as `RSETHPriceFeed (Morph)`) that computes rsETH/USD by multiplying the ETH/USD Chainlink price by the cached `rsETHPrice` stored in `LRTOracle`. However, `latestRoundData()` returns `roundId`, `startedAt`, `updatedAt`, and `answeredInRound` sourced entirely from the ETH/USD Chainlink feed — not from when `rsETHPrice` was last updated. External protocols (e.g., Morpho) that rely on `updatedAt` to detect stale prices will see a fresh timestamp from the ETH/USD feed even when the rsETH price component is hours or days old.

This is the direct analog of the external report: just as Salty used BTC/USD instead of WBTC/USD (hiding a potential depeg), `RSETHPriceFeed` uses ETH/USD freshness metadata to mask the staleness of the rsETH/ETH component.

### Finding Description

`RSETHPriceFeed.latestRoundData()` is implemented as:

```solidity
// contracts/oracles/RSETHPriceFeed.sol lines 63-70
function latestRoundData()
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

The five return values (`roundId`, `startedAt`, `updatedAt`, `answeredInRound`) all come from the ETH/USD Chainlink feed, which updates every few minutes. The `answer`, however, is computed by multiplying that ETH/USD price by `RS_ETH_ORACLE.rsETHPrice()` — a **stored state variable** in `LRTOracle`:

```solidity
// contracts/LRTOracle.sol line 28
uint256 public override rsETHPrice;
```

This value is only updated when `updateRSETHPrice()` is called:

```solidity
// contracts/LRTOracle.sol lines 87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Critically, `updateRSETHPrice()` is blocked when the oracle is paused. The oracle auto-pauses when the rsETH price drops beyond `pricePercentageLimit`:

```solidity
// contracts/LRTOracle.sol lines 277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

Once paused, `rsETHPrice` is frozen at its last value. `RSETHPriceFeed.latestRoundData()` continues to return a fresh `updatedAt` from the ETH/USD feed, making the composite rsETH/USD price appear current to any consumer that checks `updatedAt` for staleness.

### Impact Explanation

External protocols (Morpho, as confirmed by the `RSETHPriceFeed (Morph)` deployment in the README) that consume `RSETHPriceFeed` as a Chainlink-compatible oracle will check `updatedAt` to determine whether the price is fresh. Because `updatedAt` reflects the ETH/USD feed's last update (not the rsETH price's last update), these protocols will accept a stale rsETH price as current. In the scenario where rsETH price has dropped (triggering auto-pause) but the stale pre-drop price is still being served with a fresh `updatedAt`, borrowers in Morpho can borrow against overvalued rsETH collateral, creating bad debt for lenders. The contract fails to deliver the promised return of an accurate, freshness-stamped rsETH/USD price.

**Impact: Low — Contract fails to deliver promised returns.**

### Likelihood Explanation

The staleness window opens whenever `LRTOracle` is paused — either automatically (price drop exceeds `pricePercentageLimit`) or manually by the pauser role. Auto-pause is a designed safety mechanism that activates during exactly the market stress events (e.g., slashing) when accurate rsETH pricing is most critical. During such events, `RSETHPriceFeed` will serve a stale price with a fresh `updatedAt`, and external protocols have no on-chain way to detect this discrepancy.

### Recommendation

`RSETHPriceFeed.latestRoundData()` should expose the staleness of the rsETH price component. One approach is to track the timestamp of the last `rsETHPrice` update in `LRTOracle` and return the **minimum** of the ETH/USD `updatedAt` and the rsETH price's last-updated timestamp:

```solidity
// In LRTOracle: add a public lastRsETHPriceUpdate timestamp
uint256 public lastRsETHPriceUpdate;
// Set it in _updateRsETHPrice() before returning

// In RSETHPriceFeed.latestRoundData():
updatedAt = Math.min(updatedAt, RS_ETH_ORACLE.lastRsETHPriceUpdate());
```

This ensures that any consumer checking `updatedAt` against a heartbeat threshold will correctly detect when the rsETH price component is stale.

### Proof of Concept

1. rsETH price is 1.05 ETH. `LRTOracle.rsETHPrice = 1.05e18`. `pricePercentageLimit` is set to 1% (1e16).
2. A slashing event causes the true rsETH value to drop to 1.03 ETH.
3. Someone calls `updateRSETHPrice()`. `_updateRsETHPrice()` computes `newRsETHPrice ≈ 1.03e18`, detects a >1% drop from `highestRsethPrice`, and auto-pauses `LRTOracle`, `LRTDepositPool`, and `LRTWithdrawalManager`. `rsETHPrice` is **not updated** — it remains at `1.05e18`.
4. `updateRSETHPrice()` now reverts with `ContractPaused` for all callers.
5. A Morpho borrower calls `RSETHPriceFeed.latestRoundData()`. The function returns `updatedAt` from the ETH/USD Chainlink feed (e.g., 2 minutes ago) and `answer = 1.05e18 * ETH_USD / 1e18` — the stale pre-slashing price.
6. Morpho's staleness check passes (ETH/USD `updatedAt` is fresh). The borrower is allowed to borrow against rsETH valued at 1.05 ETH when the true value is 1.03 ETH, creating undercollateralized positions and potential bad debt for Morpho lenders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L26-43)
```text
contract RSETHPriceFeed is AggregatorV3Interface {
    /// @notice Price feed for (ETH / USD) pair
    AggregatorV3Interface public immutable ETH_TO_USD;

    /// @notice rsETH oracle contract
    IRSETHOracle public immutable RS_ETH_ORACLE;

    string public description;

    /// @param ethToUSDAggregatorAddress the address of ETH / USD feed
    /// @param rsETHOracle the address of rsETHOracle contract
    /// @param description_ priceFeed description (RSETH / USD)
    constructor(address ethToUSDAggregatorAddress, address rsETHOracle, string memory description_) {
        ETH_TO_USD = AggregatorV3Interface(ethToUSDAggregatorAddress);
        RS_ETH_ORACLE = IRSETHOracle(rsETHOracle);

        description = description_;
    }
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

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
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
