Audit Report

## Title
`RSETHPriceFeed.latestRoundData()` Returns Stale rsETH/USD Price with a Misleading Fresh `updatedAt` Timestamp — (File: `contracts/oracles/RSETHPriceFeed.sol`)

## Summary

`RSETHPriceFeed` computes rsETH/USD by multiplying the live ETH/USD Chainlink answer by the stored `LRTOracle.rsETHPrice`. The `updatedAt` timestamp it returns is sourced exclusively from the ETH/USD Chainlink feed. When a large price drop triggers the auto-pause path in `_updateRsETHPrice()`, `rsETHPrice` is frozen at its pre-drop value indefinitely while `updatedAt` continues to reflect the ETH/USD feed's normal ~1-hour heartbeat, making the composite price appear fresh to any consumer that relies on `updatedAt` for staleness gating.

## Finding Description

**Root cause — `rsETHPrice` is a cached value with no associated timestamp.**

`LRTOracle.rsETHPrice` is a state variable written only at the end of a successful `_updateRsETHPrice()` execution:

```solidity
// contracts/LRTOracle.sol L313
rsETHPrice = newRsETHPrice;
```

**Auto-pause path freezes `rsETHPrice` without updating it.**

When `newRsETHPrice` falls below `highestRsethPrice` by more than `pricePercentageLimit`, the function pauses the deposit pool, withdrawal manager, and oracle, then returns early — `rsETHPrice` is never reassigned:

```solidity
// contracts/LRTOracle.sol L277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;   // rsETHPrice unchanged
}
```

**`latestRoundData()` propagates only the ETH/USD feed's `updatedAt`.**

```solidity
// contracts/oracles/RSETHPriceFeed.sol L68-69
(roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
```

All metadata fields — including `updatedAt` — come from the ETH/USD feed. The stale `rsETHPrice` component has no timestamp representation in the returned tuple.

**Existing checks are insufficient.**

`updateRSETHPrice()` is gated by `whenNotPaused`, so once the oracle is paused, no unprivileged caller can refresh `rsETHPrice`. Only `updateRSETHPriceAsManager()` (restricted to `onlyLRTManager`) can update the price while paused. There is no on-chain mechanism in `RSETHPriceFeed` to detect or signal that `rsETHPrice` is stale.

**Exploit flow:**

1. EigenLayer slashing reduces protocol TVL by more than `pricePercentageLimit` (e.g., 2%).
2. Any caller invokes `LRTOracle.updateRSETHPrice()` → `_updateRsETHPrice()` pauses the protocol and returns without writing `rsETHPrice`. `rsETHPrice` remains at the pre-slashing (inflated) value.
3. The ETH/USD Chainlink feed continues updating normally; `updatedAt` is always recent.
4. Attacker calls `RSETHPriceFeed.latestRoundData()` → receives an inflated `answer` with a fresh `updatedAt`.
5. Attacker supplies rsETH as collateral to Morpho (confirmed integration: `RSETHPriceFeed (Morph)` is deployed at `0x4B9C66c2C0d3706AabC6d00D2a6ffD2B68A4E383` on ETH Mainnet per README). Morpho's staleness check passes because `block.timestamp - updatedAt` is within the heartbeat threshold.
6. Morpho prices the collateral at the stale inflated rate; attacker borrows the maximum allowed.
7. Attacker exits. True collateral value is lower by the slashing percentage; Morpho accrues bad debt borne by its liquidity providers.

## Impact Explanation

**Critical — Direct theft of user funds (Morpho LP funds).**

The `RSETHPriceFeed` is a deployed, production contract explicitly integrated with Morpho. When the auto-pause path freezes `rsETHPrice`, the feed serves an inflated price with a fresh timestamp. Any rsETH holder can exploit this to borrow against over-valued collateral, extracting funds from Morpho's liquidity providers. The loss is permanent and proportional to the slashing magnitude multiplied by the attacker's collateral position size.

## Likelihood Explanation

**Medium.** EigenLayer slashing is a live, protocol-acknowledged risk — the `pricePercentageLimit` guard exists precisely to respond to it. A single significant slashing event on a delegated operator is sufficient to trigger the freeze. No privileged access is required: any rsETH holder can supply collateral to Morpho and borrow against the stale price. The trigger is uncommon but realistic and has occurred in analogous restaking protocols.

## Recommendation

1. **Track the rsETH price update timestamp.** Add `uint256 public rsETHPriceUpdatedAt` to `LRTOracle` and set it to `block.timestamp` every time `rsETHPrice` is written (line 313).

2. **Expose the timestamp via the oracle interface.** Add a `rsETHPriceUpdatedAt()` getter to `IRSETHOracle` and implement it in `LRTOracle`.

3. **Return the correct `updatedAt` in `RSETHPriceFeed`.** Replace the raw ETH/USD `updatedAt` with `min(ethToUsdUpdatedAt, RS_ETH_ORACLE.rsETHPriceUpdatedAt())` so consumers see the true age of the composite price.

4. **Add an explicit staleness revert.** Inside `latestRoundData()`, revert if `block.timestamp - rsETHPriceUpdatedAt` exceeds a configurable maximum age (e.g., 24 hours).

## Proof of Concept

```
// Foundry fork test outline
// 1. Fork mainnet; set pricePercentageLimit = 2e16 (2%)
// 2. Manipulate underlying asset prices to simulate a 3% TVL drop
//    (or directly set rsETHPrice via storage slot for unit test)
// 3. Call LRTOracle.updateRSETHPrice()
//    → Assert: protocol is paused
//    → Assert: rsETHPrice unchanged (still pre-drop value)
// 4. Advance block.timestamp by 2 hours (ETH/USD feed will have updated)
// 5. Call RSETHPriceFeed.latestRoundData()
//    → Assert: updatedAt is within last hour (appears fresh)
//    → Assert: answer reflects the stale, inflated rsETHPrice
// 6. Demonstrate Morpho staleness check passes:
//    → block.timestamp - updatedAt < Morpho's maxStaleness threshold
// 7. Show borrow capacity exceeds true collateral value by ~3%
```

Precondition: `pricePercentageLimit = 2e16`, `rsETHPrice = 1.05e18`, `highestRsethPrice = 1.05e18`.
- Slashing causes `newRsETHPrice ≈ 1.0185e18` (−3%).
- `diff = 0.0315e18 > 2% × 1.05e18 = 0.021e18` → `isPriceDecreaseOffLimit = true`.
- Protocol pauses; `rsETHPrice` stays at `1.05e18`.
- ETH/USD feed updates normally; `updatedAt = block.timestamp − 10 minutes`.
- `RSETHPriceFeed.latestRoundData()` returns `answer = 1.05e18 × ETH_USD / 1e18` (inflated ~3%) with fresh `updatedAt`.
- Attacker borrows against this price in Morpho; Morpho accrues ~3% bad debt per unit of rsETH collateral. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
