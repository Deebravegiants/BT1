# [M] No way to cancel l1 -< l2 messages 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-kakarot
Published: 2024-10-28
Source: https://github.com/code-423n4/2024-09-kakarot-findings/issues/105
Type: code-finding

## Details
# Lines of code

https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/solidity_contracts/src/L1L2Messaging/L1KakarotMessaging.sol#L26-L61


# Vulnerability details

## Description
There is no api to allow cancellation of l1->l2 messages. In the event of an issue in the kakarot contracts, this will result in the fee being permanently lost since the user has no ability to reclaim the funds.
https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/solidity_contracts/src/L1L2Messaging/L1KakarotMessaging.sol#L26-L61
As we can see there are only functions to either send the message from l1 -> l2 or consume an l2 message. There is no `cancelL1toL2Message` present.
## Recommended Mitigation Steps
https://docs.starknet.io/architecture-and-concepts/network-architecture/messaging-mechanism/#l2-l1_message_cancellation
Introduce the following API to let users cancel their messages after waiting the time limit so that they can reclaim funds. 


## Assessed type

Context
