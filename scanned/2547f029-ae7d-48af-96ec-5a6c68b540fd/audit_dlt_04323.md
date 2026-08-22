# [M] Cross-chain replay attacks are possible with `createStream()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/34
Type: sherlock-finding

## Details
0xSmartContract

medium

# Cross-chain replay attacks are possible with `createStream()`

## Summary
[StreamFactory.sol#L202](https://github.com/sherlock-audit/2022-11-nounsdao/blob/main/src/StreamFactory.sol#L202)

Mistakes made on one chain can be re-applied to a new chain

There is no chain.id in the createStream() function data

```solidity
stream = streamImplementation.cloneDeterministic(
            encodeData(payer, recipient, tokenAmount, tokenAddress, startTime, stopTime),
            salt(
                msg.sender, payer, recipient, tokenAmount, tokenAddress, startTime, stopTime, nonce
            )
```

## Vulnerability Detail
Mistakes made on one chain can be re-applied to a new chain

There is no chain.id in the createStream() function data



## Impact
If a user does `createStream() ` using the wrong network, an attacker can replay the action on the correct chain, and steal the funds a-la the wintermute gnosis safe attack, where the attacker can create the same address that the user tried to, and steal the funds from there


https://mirror.xyz/0xbuidlerdao.eth/lOE5VN-BHI0olGOXe27F0auviIuoSlnou_9t3XRJseY


## Code Snippet
[StreamFactory.sol#L202](https://github.com/sherlock-audit/2022-11-nounsdao/blob/main/src/StreamFactory.sol#L184-L213)


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/34_
