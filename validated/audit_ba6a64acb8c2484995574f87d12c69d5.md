Audit Report

## Title
`RSETHPriceFeed.latestRoundData()` Returns Stale rsETH/USD Price with Misleading Fresh `updatedAt` Timestamp — (File: `contracts/oracles/RSETHPriceFeed.sol`)

## Summary

`RSETHPriceFeed.latestRoundData()` computes rsETH/USD by multiplying the live ETH/USD Chainlink answer by `LRTOracle.rsETHPrice`, but returns `updatedAt` sourced exclusively from the ETH/USD feed. When a large price drop triggers the auto-pause path in `_updateRsETHPrice()`, `rsETHPrice` is frozen at its pre-drop value indefinitely while `updatedAt` continues to reflect the ETH/USD feed's normal ~1-hour heartbeat. Any integrated lending protocol (e.g., Morpho, referenced in the README) that gates staleness on `updatedAt` will accept the inflated price as fresh, enabling an attacker to borrow against over-valued rsETH collateral.

## Finding Description

**Root cause — `rsETHPrice` is a cached value with no independent timestamp.**

`LRTOracle.rsETHPrice` is a plain state variable written only at the end of `_updateRsETHPrice()`. [1](#0-0) [2](#0-1) 

**Auto-pause path returns early without writing `rsETHPrice`.**

When `newRsETHPrice` drops more than `pricePercentageLimit` below `highestRsethPrice`, the function pauses the deposit pool, withdrawal manager, and oracle, then executes `return` at line 281 — before the `rsETHPrice = newRsETHPrice` assignment at line 313. The stale (higher) value persists indefinitely. [3](#0-2) 

Additionally, `updateRSETHPrice()` is gated by `whenNotPaused`, so once the protocol is paused, no unprivileged caller can update the price at all. [4](#0-3) 

**`latestRoundData()` propagates the ETH/USD `updatedAt` unchanged.**

All five return values — including `updatedAt` — are taken directly from `ETH_TO_USD.latestRoundData()`. Only `answer` is replaced with the product of the stale `rsETHPrice` and the live ETH/USD price. The ETH/USD feed updates on its own ~1-hour heartbeat regardless of the rsETH/ETH component's age. [5](#0-4) 

**No guard prevents consumption of the stale composite price.**

There is no staleness check, no circuit breaker, and no mechanism inside `RSETHPriceFeed` to detect or signal that `rsETHPrice` has not been updated. The contract is a pure view function with no state of its own. [6](#0-5) 

## Impact Explanation

**Critical — Direct theft of user funds.**

After a slashing event freezes `rsETHPrice` at the pre-loss value, an attacker holding rsETH can supply it as collateral to Morpho (or any integrated lending protocol) at the inflated price. Because `updatedAt` appears fresh, Morpho's standard staleness check passes and it allows maximum borrowing against the over-valued collateral. The attacker exits with borrowed assets; the lending protocol accrues bad debt borne by its liquidity providers. This is direct, concrete theft of funds in motion through a supported, documented integration path.

## Likelihood Explanation

EigenLayer slashing is a live, protocol-acknowledged risk — the `pricePercentageLimit` guard exists precisely to respond to it. A single significant slashing event on a delegated operator is sufficient to trigger the auto-pause and freeze `rsETHPrice`. The attack requires no privileged access: any rsETH holder can supply collateral to Morpho and borrow against the stale price. Likelihood is **Medium** — the trigger is uncommon but realistic and has occurred in analogous restaking protocols.

## Recommendation

1. **Track the rsETH price update timestamp.** Add `uint256 public rsETHPriceUpdatedAt` to `LRTOracle` and set it to `block.timestamp` every time `rsETHPrice` is written (line 313).

2. **Return the correct `updatedAt` in `RSETHPriceFeed`.** Replace the raw ETH/USD `updatedAt` with `min(ethToUsdUpdatedAt, rsETHPriceUpdatedAt)` so consumers see the true age of the composite price.

3. **Add an explicit staleness revert.** Inside `latestRoundData()`, revert if `block.timestamp - rsETHPriceUpdatedAt` exceeds a configurable maximum age (e.g., 24 hours), consistent with the expected oracle heartbeat.

## Proof of Concept

```
Precondition: pricePercentageLimit = 2e16 (2%), rsETHPrice = 1.05e18, highestRsethPrice = 1.05e18.

1. EigenLayer slashing reduces protocol TVL by 3%.

2. Anyone calls LRTOracle.updateRSETHPrice().
   → newRsETHPrice ≈ 1.0185e18 (−3% from peak).
   → diff = 1.05e18 − 1.0185e18 = 0.0315e18 > 2% × 1.05e18 = 0.021e18.
   → isPriceDecreaseOffLimit = true.
   → _pause() called; function returns at line 281 WITHOUT executing line 313.
   → rsETHPrice remains 1.05e18.
   → updateRSETHPrice() is now blocked by whenNotPaused for all non-manager callers.

3. ETH/USD Chainlink feed updates normally (updatedAt = block.timestamp − 10 minutes).

4. Attacker calls RSETHPriceFeed.latestRoundData().
   → updatedAt = ETH/USD updatedAt (10 minutes ago — passes any reasonable staleness check).
   → answer = 1.05e18 × ETH_USD_price / 1e18  (inflated ~3% above true value).

5. Attacker supplies rsETH to Morpho; Morpho reads RSETHPriceFeed, sees fresh updatedAt,
   accepts the inflated price, and allows maximum borrowing.

6. Attacker borrows against over-valued collateral and exits.
   True collateral value is ~3% lower; Morpho accrues bad debt at the expense of its LPs.
```

### Citations

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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

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
