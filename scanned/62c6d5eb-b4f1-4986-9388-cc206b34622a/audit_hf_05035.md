# [M] UniswapV3PoolTwapObserver uses the slot0

## Summary
Severity: Medium
Contest weight: 0.5928
Dataset id: 23039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UniswapV3PoolTwapObserver uses the slot0 price when duration is zero, which is manipulable. Attackers can exploit this to buy tokens nearly for free.
Background
First, we need to understand how moving liquidity works. Each time a user calls move liquidity, all the inTokens up to the current timestamp need to be swapped.
During the move liquidity process, a new checkpoint is created in the UniswapV3PoolTwapObserver to update the timestamp.
The core issue here is that if the duration is zero for the current liquidity movement from the last liquidity movement, the UniswapV3PoolTwapObserver defaults to using the spot price in slot0, which is manipulable.
At first glance, it might seem that if the duration is zero, all inTokens would have already been swapped in the last liquidity movement, leaving no tokens to move for this liquidity movement. However, there is a way to get some tokens.
Notice that the availableInTokens() function calculates the amount of inTokens left for this round of liquidity movement by _inToken.balanceOf(address(this)) - minimumDeposit. There is a concept of minimumDeposit, calculated by uint256 minimumDeposit = _inToken.getBufferAmountByFlowRate(_requestedFeeDistFlowRate);. This is the amount of tokens that needs to be in Torex to maintain the outflow for the feeDistributionPool. If a user decreases their flowRate, the minimumDeposit decreases, and an attacker could perform a sandwich attack to buy these tokens at a very cheap price.
The deposit amount can be found in ConstantFlowAgreementV1.sol. It is basically the flowRate multiplied by the liquidationPeriod (which is 4 hours), so a flowRate of 1e18 would mean a deposit amount of 14400e18.
Attack vector
To sum it up, the attacker would monitor the mempool and find a user with flowRate X closing their flow. The attack vector is:
Before the transaction:
1. The attacker calls moveLiquidity for the first time, moving the remaining inTokens in Torex.
2. The attacker manipulates the Uniswap slot0 spot price by swapping a large number of tokens.
Transaction is executed, and the user closes their flow. Now, there are 14400X more available tokens in Torex.
After the transaction:
1. The attacker calls moveLiquidity again and buys 14400X tokens at a very cheap price, since it uses the Uniswap slot0 spot price as the oracle.
2. The attacker restores the Uniswap spot price.
Additionally, anyone can use this method to buy back their backcharged tokens that were spent as a deposit for the fee flow at a cheap price. In that case, the backcharged fees are not refunded if the flowRate decreases: // however, in case of the flow rate going down, there is no refund for back charged fees..
However, using this attack method, users can get their backcharged fees back.
```solidity
UniswapV3PoolTwapObserver.sol
function getTwapSinceLastCheckpoint(uint256 time, uint256 inAmount) public override view
returns (uint256 outAmount, uint256 duration)
{
    duration = getDurationSinceLastCheckpoint(time);
    int24 tick;
    if (duration > 0) {
        // calculating tick of the TWAP
        int56 currentTickCumulative = _getCurrentTickCumulative();
        tick = SafeCast.toInt24((int256(currentTickCumulative) - int256(_lastTickCumulative))
        / SafeCast.toInt256(duration));
    } else {
        // special case: when duration is zero, returning the current tick directly
        (/*sqrtPriceX96*/,tick,/*obsIdx*/,/*obsCrd*/,/*obsCrdNext*/,/*feeP*/,/*unlckd*/) = uniPool.slot0();
    }
    //
    1. OracleLibrary.getQuoteAtTick(int24 tick, uint128 baseAmount, address baseToken, address quoteToken)
    //
    baseAmount of baseToken."
    //
    1.1 TickMath.getSqrtRatioAtTick(int24 tick) returns (uint160 sqrtPriceX96)
    if (inverseOrder == false) {
        outAmount = OracleLibrary.getQuoteAtTick(tick, SafeCast.toUint128(inAmount), uniPool.token0(), uniPool.token1());
    } else {
        outAmount = OracleLibrary.getQuoteAtTick(tick, SafeCast.toUint128(inAmount), uniPool.token1(), uniPool.token0());
    }
}
```
```solidity
TorexCore.sol
function _moveLiquidity(bytes memory moverData) internal nonReentrant returns (LiquidityMoveResult memory result)
{
    (result.inAmount, result.minOutAmount, result.durationSinceLastLME, result.twapSinceLastLME) =
    getLiquidityEstimations();
    // Step 1: Transfer the inAmount of inToken liquidity to the liquidity mover.
    _inToken.transfer(msg.sender, result.inAmount);
    // Step 2: Ask liquidity mover to provide outAmount of outToken liquidity in exchange.
    assert((ILiquidityMover(msg.sender)).moveLiquidityCallback(_inToken, _outToken, result.inAmount, result.minOutAmount, moverData));
    // We distribute everything the contract has got from liquidity mover.
    result.outAmount = _outToken.balanceOf(address(this));
    if (result.outAmount < result.minOutAmount) revert LIQUIDITY_MOVER_SENT_INSUFFICIENT_OUT_TOKENS();
    // Step 3: Create new torex observer check point
    _observer.createCheckpoint(block.timestamp);
    // Step 4: Distribute all outToken liquidity to degens.
    result.actualOutAmount = _outToken.estimateDistributionActualAmount(address(this), _outTokenDistributionPool, result.outAmount);
    _outToken.distributeToPool(address(this), _outTokenDistributionPool, result.actualOutAmount);
}
function getLiquidityEstimations() public view returns (uint256 inAmount, uint256 minOutAmount, uint256 durationSinceLastLME, uint256 twapSinceLastLME)
{
    inAmount = availableInTokens();
    (minOutAmount, durationSinceLastLME, twapSinceLastLME) = getBenchmarkQuote(inAmount);
}
```
```solidity
Torex.sol
function availableInTokens() override internal view returns (uint256 amount)
{
    uint256 minimumDeposit = _inToken.getBufferAmountByFlowRate(_requestedFeeDistFlowRate);
    amount = _inToken.balanceOf(address(this));
    if (amount >= minimumDeposit) return amount - minimumDeposit; else return 0;
}
```
1. For a normal user, anyone can use this method to buy back their backcharged tokens that were spent as a deposit for the fee flow at a cheap price.
2. For an attacker, they can perform a sandwich attack to buy tokens at a very cheap price.

## Recommendation
Always use the TWAP price in UniswapV3PoolTwapObserver to avoid price
