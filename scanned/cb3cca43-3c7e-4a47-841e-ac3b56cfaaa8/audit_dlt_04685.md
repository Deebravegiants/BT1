# [H] Free Voting power without locking token

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/77
Type: sherlock-finding

## Details
csanuragjain

high

# Free Voting power without locking token

## Summary
It was observed that user can stake such that locking and unlock time remain the same. Now even in this situation getTokenVotingPower will return 10 votes even though user is not locking his token for any duration

## Vulnerability Detail

1. User A stakes _tokenIds T1 with _unlockTime as block.timestamp in Transaction T1
2. This gets passed since below statement only fails when

```solidity
_unlockTime < block.timestamp
```

3. Within same transaction T1 User A votes. Ideally his voting power should come as 0 but instead it comes as 10 since ` ((baseVotes * multiplier) / PERCENT)` becomes `20*50/100 =10`

```solidity
function getTokenVotingPower(uint _tokenId) public override view returns (uint) {
      ...
      return ((baseVotes * multiplier) / PERCENT) + stakedTimeBonus[_tokenId] + evilBonus(_tokenId);
    }
```

4. Now after voting with his 10 power user simply unstakes which also works since block.timestamp is the unlock period
5. Hence user has staked - voted with 10 free votes - unstaked without actually locking any token

## Impact
User get free votes even without locking tokens

## Code Snippet
https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Staking.sol#L514

## Tool used
Manual Review

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/77_
