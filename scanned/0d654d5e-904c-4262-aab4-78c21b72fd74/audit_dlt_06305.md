# [M] processPacket and recoverAck can fail due to Wormhole guardian change

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-04
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/81
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x390d31b6ea8525b68816e59f75b266f94439726e7849a8cc911a673e2bd75345
**Severity:** medium

**Description:**
**Description**\
Wormhole governance can change signing guardian sets. As the application sets the incentive for the relayer to deliver the message, and gas prices can spike and remain high for a longer period of time, the relayer could be witholding the delivery of message.
If during this time the Wormhole guardian set changes the message cannot be delivered.

**Attack Scenario**\
During the delivery of a message [_verifyPacket](https://github.com/catalystdao/GeneralisedIncentives/blob/2448d77e412216283ed75d8c3cbaa1270657f7b5/src/apps/wormhole/IncentivizedWormholeEscrow.sol#L39) gets called. 
One of the checks is to verify the guardian set: https://github.com/catalystdao/GeneralisedIncentives/blob/2448d77e412216283ed75d8c3cbaa1270657f7b5/src/apps/wormhole/external/callworm/WormholeVerifier.sol#L56.
But Wormhole can change the guardian set at any moment: https://github.com/wormhole-foundation/wormhole/blob/main/ethereum/contracts/Governance.sol#L76-L112. After the change the existing signatures can only be used for 1 day: https://github.com/wormhole-foundation/wormhole/blob/main/ethereum/contracts/Setters.sol#L13, as expiration time is set.

If message is not delivered during this period the verification will fail, and it can no longer be delivered.

This is a problem with the whole incentive mechanism as the sending application sets the gas price but gas prices can spike and remain high for extended periods of time. During which time the relayer is not going to deliver the message. 

**Potential fix**\
The `IncentivizedWormholeEscrow` contract needs to have a way of reverting the state on the sending chain if the acknowledgment cannot be delivered. 
Also, there should be maximum delivery time specified.
