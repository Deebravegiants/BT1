# [H] Interchain Security: The signers of ICS messages do not need to match the provider address 

## Summary
Severity: High
Chain: github.com/cosmos/interchain-security/v5
Component: github.com/cosmos/interchain-security/v5, github.com/cosmos/interchain-security, github.com/cosmos/interchain-security/v
Published: 2024-09-05
Source: https://github.com/advisories/GHSA-7q74-g774-7x3g
Type: github-advisory

## Details
### Context

ICS has the following four messages that enable validators on the provider chain to perform different actions:

- `MsgOptIn` -- adds a validator to the consumer chain’s active set
- `MsgOptOut` -- removes a validator from the consumer chain’s active set 
- `MsgAssignConsumerKey` -- changes the consensus key used for a validator’s operations on a consumer chain
- `MsgSetConsumerCommissionRate` -- sets a validator’s consumer-specific commission rate

Normally, only the respective validators are allowed to perform these actions. 

### Issue

The upgrade to SDK 0.50, introduced a [signer](https://docs.cosmos.network/v0.50/build/building-modules/protobuf-annotations#signer) field to these messages. This field is used to authenticate the user sending the message to the system. However, there was no validation on the ICS side to check if the signer matches the provider address.  

As a result, any user could opt-in, opt-out, change the commission rate, or change what public key a validator uses on a consumer chain. 

For more context, check out the code:

- proto files https://github.com/cosmos/interchain-security/blob/v5.1.1/proto/interchain_security/ccv/provider/v1/tx.proto#L52
- message validation https://github.com/cosmos/interchain-security/blob/v5.1.1/x/ccv/provider/types/msg.go#L106
- message handling https://github.com/cosmos/interchain-security/blob/v5.1.1/x/ccv/provider/keeper/msg_server.go#L52

### Severity assessment

The severity assessment is based on [this framework](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md). 

**Potential impact:** Catastrophic 

- By changing consumer keys for 1/3+ of a consumer chain's validator set, any user could cause a consumer chain to halt. Given that the consumer is down, the provider will jail provider validators for consumer downtime, so this exploit would not have impacted the provider directly. Consumer chain halts would need to be addressed by a provider-side patch.
- By changing consumer keys on a consumer node, double signing, and submitting evidence back to the provider, any user could tombstone any provider validator. This would cause the provider's active set to change. At scale, this exploit could be applied to all active provider validators and a well-funded attacker could then run their own nodes and take over consensus on the provider and on consumer chains.

**Likelihood:** Rare

- The bug was discovered internally. There is no evidence that any external party has identified this vulnerability. 
- The bug has been live for two weeks with no issues. 
- All four message types are ones that only validators use, and rarely use in daily operations.
- In the Cosmos Hub’s recent history (May - Aug), there has been only one instance of any of these message types, which was performed in accordance with chain rules.

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-7q74-g774-7x3g_
