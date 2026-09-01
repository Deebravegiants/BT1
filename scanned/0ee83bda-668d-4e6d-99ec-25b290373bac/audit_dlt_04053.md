# [M] Boosted Balancer Leverage Vault Might Not Be Able To Exit Its Position

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/93
Type: sherlock-finding

## Details
xiaoming90

medium

# Boosted Balancer Leverage Vault Might Not Be Able To Exit Its Position

## Summary

The boosted balancer leverage vault might not be able to exit its position under certain conditions as the BPT threshold check was not performed against all the involved Balancer pools.

## Vulnerability Detail

Per the Notional walkthrough video (see [4:11min](https://youtu.be/YbtM6dzFRVs?t=251)), the reason for having the BPT threshold is to ensure that the strategy does not hold too large of a share of the liquidity within the pool. Otherwise, the strategy will have a problem exiting its position.

At Line 335-342, if the number of BPT the vault held within a pool after joining exceeds the BPT threshold, the code will revert.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/internal/pool/Boosted3TokenPoolUtils.sol#L325

```solidity
File: Boosted3TokenPoolUtils.sol
325:     function _joinPoolAndStake(
326:         ThreeTokenPoolContext memory poolContext,
327:         StrategyContext memory strategyContext,
328:         AuraStakingContext memory stakingContext,
329:         BoostedOracleContext memory oracleContext,
330:         uint256 deposit,
331:         uint256 minBPT
332:     ) internal returns (uint256 bptMinted) {
333:         bptMinted = _joinPoolExactTokensIn(poolContext, deposit, minBPT);
334: 
335:         // Check BPT threshold to make sure our share of the pool is
336:         // below maxBalancerPoolShare
337:         uint256 bptThreshold = strategyContext.vaultSettings._bptThreshold(
338:             poolContext._getVirtualSupply(oracleContext)
339:         );
340:         uint256 bptHeldAfterJoin = strategyContext.totalBPTHeld + bptMinted;
341:         if (bptHeldAfterJoin > bptThreshold)
342:             revert Errors.BalancerPoolShareTooHigh(bptHeldAfterJoin, bptThreshold);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/93_
