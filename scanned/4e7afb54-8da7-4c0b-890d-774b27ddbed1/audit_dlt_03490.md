# [H] Disabling outbound transactions is ineffective and allows for Zeta token theft

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/414
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L452
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L530-L544


# Vulnerability details

## Impact

Outbound EVM transactions can not be disabled and will be wrongly sent out, either stealing Zeta tokens or manifesting in a loss for users who attempt to withdraw gas or ERC-20 tokens.

## Proof of Concept

In lines [`530-544` of the `TryProcessOutTx` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L530-L544), called by the observer's EVM signer to send an outbound cctx transaction to the receiver chain, the [`SignOutboundTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L140-L168) function is invoked to sign the transaction tx.

This transaction has the [Zeta connector contract as the `to` address and the ABI encoded `onReceive` function call as the calldata](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L157-L162). As a result, the connector contract, e.g., the `ZetaConnectorEth` contract, has the `onReceive` function called and [subsequently transfers Zeta tokens to the `destinationAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L60).

Now let's re-visit a critical part of the `TryProcessOutTx` function, specifically, lines [`439-544`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L439-L544):

```go
439: 	if send.GetCurrentOutTxParam().CoinType == common.CoinType_Cmd { // admin command
... 		// [...]
452: 	} else if send.InboundTxParams.SenderChainId == common.ZetaChain().ChainId && send.CctxStatus.Status == types.CctxStatus_PendingOutbound && flags.IsOutboundEnabled {
453: 		if send.GetCurrentOutTxParam().CoinType == common.CoinType_Gas {
... 			  // [...]
462: 		}
463: 		if send.GetCurrentOutTxParam().CoinType == common.CoinType_ERC20 {
... 			  // [...]
475: 		}
476: 		if send.GetCurrentOutTxParam().CoinType == common.CoinType_Zeta {
... 			  // [...]
490: 		}
491: 	} else if send.CctxStatus.Status == types.CctxStatus_PendingRevert && send.OutboundTxParams[0].ReceiverChainId == common.ZetaChain().ChainId {
... 		// [...]
515: 	} else if send.CctxStatus.Status == types.CctxStatus_PendingRevert {
... 		// [...]
530: 	} else if send.CctxStatus.Status == types.CctxStatus_PendingOutbound {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/414_
