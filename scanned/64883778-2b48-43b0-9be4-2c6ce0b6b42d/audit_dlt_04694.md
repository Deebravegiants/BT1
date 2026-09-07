# [M] Expired locks should not continue to get `stakedTimeBonus` at the original lock time

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/58
Type: sherlock-finding

## Details
WATCHPUG

medium

# Expired locks should not continue to get `stakedTimeBonus` at the original lock time

## Summary

Expired lock should be considered as same as the stake with no lock.

## Vulnerability Detail

`stakedTimeBonus` is a majority part of `TokenVotingPower`:

The `baseVotes` is `20` and `maxStakeBonusAmount` for a 4 weeks lock is also `20`, and the evil bonus is only `10`.

The current implementation allows the deposits with expired locks to continue to enjoy the original high staked time bonus, while they can unstake anytime they want.

## Impact

Unlocked NFTs can continue to get max `stakedTimeBonus` and amplify their `TokenVotingPower`.

## Code Snippet

https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Staking.sol#L389-L415


## Tool used

Manual Review

## Recommendation

Curve's Gauge system introcuded a method called `kick()` which allows the expired (zeroed) veCRV users to be kicked from the rewards.

See: https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV5.vy#L430-L446

A similar method can be added to solve this issue:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/58_
