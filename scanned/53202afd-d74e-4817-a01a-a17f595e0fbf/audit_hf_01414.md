# [H] apr circuit breaker can be avoided

## Summary
Severity: High
Contest weight: 0.3803
Dataset id: 7289
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The check in _addLiquidity only compares the current spot apr to the weightedSpotAPR of the latest checkpoint:
// Enforce the slippage guard.
uint256 apr = HyperdriveMath.calculateSpotAPR(
_effectiveShareReserves(),
_marketState.bondReserves,
_initialVaultSharePrice,
_positionDuration,
_timeStretch
);
// ...
// Perform a checkpoint.
uint256 latestCheckpoint = _latestCheckpoint();
_applyCheckpoint(
latestCheckpoint,
vaultSharePrice,
LPMath.SHARE_PROCEEDS_MAX_ITERATIONS
);
// Ensure that the spot APR is close enough to the previous weighted
// spot price to fall within the tolerance.
{
uint256 weightedSpotAPR = HyperdriveMath.calculateAPRFromPrice(
_checkpoints[latestCheckpoint].weightedSpotPrice,
_positionDuration
);
if (
apr > weightedSpotAPR + _circuitBreakerDelta ||
(weightedSpotAPR > _circuitBreakerDelta &&
apr < weightedSpotAPR - _circuitBreakerDelta)
) {
revert IHyperdrive.CircuitBreakerTriggered();
}
}
1. Big price movements across checkpoint boundaries.
But there could be big movements on the curve just before the current checkpoint start time, for example opening a max short. These price movements would not get included in the weighted spot price calculation of the next checkpoint and this:
• Big price/apr/curve movement and...
• _addLiquidity trades can happen with a short time difference (1 seconds or smallest delay between blocks) and circuit breaker logic can be avoided.
For example, apply the following patch to test/integrations/hyperdrive/SandwichTest.t.sol:
diff --git a/test/integrations/hyperdrive/SandwichTest.t.sol b/test/integrations/hyperdrive/SandwichTest.t.sol
index 6c54eadf..78fcf38a 100644
--- a/test/integrations/hyperdrive/SandwichTest.t.sol
+++ b/test/integrations/hyperdrive/SandwichTest.t.sol
@@ -385,6 +385,9 @@ contract SandwichTest is HyperdriveTest {
2 * hyperdrive.getPoolConfig().minimumShareReserves;
+
// Most of the term passes and no interest accrues.
+
advanceTime(POSITION_DURATION - 1 seconds, 0);
+
// Celine opens a large short.
shortAmount = shortAmount.normalizeToRange(
hyperdrive.getPoolConfig().minimumTransactionAmount,
@@ -392,6 +395,9 @@ contract SandwichTest is HyperdriveTest {
);
openShort(celine, shortAmount);
+
// Rest of the term passes and no interest accrues.
+
advanceTime(1 seconds, 0);
+
// Celine adds liquidity.
vm.stopPrank();
vm.startPrank(celine);
2. Price movements:
1. Perform the max short (or almost the max amount) on the checkpoint start time.
2. Wait a block
3. Perform a tiny trade that would only move the point p on the curve C a little.
4. Add liquidity's circuit breaker does not get triggered since the weighted average spot price would be the exact spot price right after the max short trade in step 1.
See the issue regarding "weightedSpotPrice".
diff --git a/test/integrations/hyperdrive/SandwichTest.t.sol b/test/integrations/hyperdrive/SandwichTest.t.sol
index 6c54eadf..09724bd8 100644
--- a/test/integrations/hyperdrive/SandwichTest.t.sol
+++ b/test/integrations/hyperdrive/SandwichTest.t.sol
@@ -387,11 +387,15 @@ contract SandwichTest is HyperdriveTest {
// Celine opens a large short.
shortAmount = shortAmount.normalizeToRange(
- hyperdrive.getPoolConfig().minimumTransactionAmount,
- hyperdrive.calculateMaxShort()
+ 2 * hyperdrive.getPoolConfig().minimumTransactionAmount,
+ hyperdrive.calculateMaxShort() - hyperdrive.getPoolConfig().minimumTransactionAmount
);
openShort(celine, shortAmount);
+
// let one block pass
+
advanceTime(12 seconds, 0);
+
openShort(celine, hyperdrive.getPoolConfig().minimumTransactionAmount);
+
// Celine adds liquidity.
vm.stopPrank();
vm.startPrank(celine);

## Recommendation
One can avoid the above issues by using a moving window weighted average price or make sure some form of weighted average apr of the previous checkpoint is included in the circuit breaker.
