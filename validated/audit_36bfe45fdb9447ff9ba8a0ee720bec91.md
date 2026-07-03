Audit Report

## Title
Stale Cross-Chain rsETH/ETH Rate Used for L2 Minting Without Freshness Check — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` without checking `block.timestamp - lastUpdated`, despite `lastUpdated` being recorded on every update. All L2 pool contracts use this rate as the denominator when computing rsETH to mint, so a stale (lower-than-current) rate causes over-minting. Because rsETH is yield-bearing and its L1 price only increases, any depositor acting during a staleness window receives more rsETH than their ETH warrants, diluting accrued yield from all existing holders.

## Finding Description
`CrossChainRateReceiver` stores both `rate` and `lastUpdated` but `getRate()` returns `rate` unconditionally:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L102-105
function getRate() external view returns (uint256) {
    return rate;   // lastUpdated is never consulted
}
```

The rate is only refreshed when someone calls `MultiChainRateProvider.updateRate()` on L1 and pays the LayerZero cross-chain gas fee — a permissionless but cost-bearing action with no on-chain enforcement of a maximum interval. During any gap, `rate` drifts below the true L1 rsETH price.

Every L2 pool contract delegates to this function through its `rsETHOracle`:

- `RSETHPoolNoWrapper.getRate()` → `IOracle(rsETHOracle).getRate()` → `CrossChainRateReceiver.getRate()`
- `RSETHPoolV3.viewSwapRsETHAmountAndFee()` → `getRate()` → same path
- Same pattern in `RSETHPool`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`

The minting formula in every pool is:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

A stale (lower) denominator produces a larger `rsETHAmount`. The contrast with `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which explicitly reverts on `answeredInRound < roundID`, confirms the team applies staleness guards elsewhere but omitted them on the cross-chain rate path.

## Impact Explanation
When the L2 oracle rate lags the true L1 rsETH price, every depositor receives excess rsETH backed by no additional ETH. This excess is redeemable on L1 at the true (higher) rate, extracting ETH value that was accrued as yield by existing rsETH holders. This is a concrete, repeatable **theft of unclaimed yield** (High severity per the allowed impact scope). The magnitude scales with deposit size and degree of staleness; a sophisticated actor monitoring the staleness window can extract meaningful value with no special permissions.

## Likelihood Explanation
`updateRate()` is permissionless but requires the caller to pay LayerZero cross-chain messaging fees. There is no keeper, no on-chain heartbeat requirement, and no circuit-breaker that pauses deposits when the rate is stale. During high gas prices, network congestion, or keeper downtime, the rate can remain stale for hours or days. rsETH yield accrues continuously (~3–5% APY), so even a few hours of staleness creates a profitable window. Any L2 depositor can exploit this with a single `deposit()` call.

## Recommendation
Add a configurable `maxStaleness` threshold to `CrossChainRateReceiver.getRate()`:

```solidity
uint256 public maxStaleness; // e.g., 86400 (24 hours)

function getRate() external view returns (uint256) {
    if (block.timestamp - lastUpdated > maxStaleness) revert StaleRate();
    return rate;
}
```

Pair this with an automated keeper that calls `updateRate()` on a regular cadence well within `maxStaleness`. Alternatively, each pool contract can check `CrossChainRateReceiver.lastUpdated` directly before using the rate.

## Proof of Concept

1. At time T, the true L1 rsETH price is 1.05 ETH/rsETH. `CrossChainRateReceiver.rate` was last set 48 hours ago at 1.03 ETH/rsETH; no one has called `updateRate()` since.
2. Attacker calls `deposit{value: 1050 ether}("")` on `RSETHPoolNoWrapper` (or any L2 pool).
3. `viewSwapRsETHAmountAndFee(1050e18)` calls `getRate()` → returns stale `1.03e18`.
4. `rsETHAmount = 1050e18 * 1e18 / 1.03e18 ≈ 1019.4e18` rsETH. At the true rate the correct amount is `1050/1.05 = 1000` rsETH.
5. Attacker receives ~19.4 rsETH in excess of fair value.
6. Attacker bridges rsETH to L1 and redeems at the true rate of 1.05 ETH/rsETH, extracting ~20.4 ETH of value diluted from existing holders.

**Foundry fork test outline:**
```solidity
// Fork L2 at a block where lastUpdated is >24h old
// Call rsETHPoolNoWrapper.deposit{value: 1050 ether}("")
// Assert rsETH received > 1000e18
// Assert CrossChainRateReceiver.lastUpdated < block.timestamp - 86400
```