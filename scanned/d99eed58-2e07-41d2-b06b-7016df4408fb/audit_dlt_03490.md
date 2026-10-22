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
... 		// [...]
532: 		tx, err = signer.SignOutboundTx(
533: 			ethcommon.HexToAddress(send.InboundTxParams.Sender),
534: 			big.NewInt(send.InboundTxParams.SenderChainId),
535: 			to,
536: 			send.GetCurrentOutTxParam().Amount.BigInt(),
537: 			gasLimit,
538: 			message,
539: 			sendhash,
540: 			send.GetCurrentOutTxParam().OutboundTxTssNonce,
541: 			gasprice,
542: 			height,
543: 		)
544: 	}
```

Here, the type of transaction signature is determined, based on the coin type, the originator (`SenderChainId`), and the status of the cctx.

The possible states are as follows (the order is important):

1. Line 439: Admin command
2. Line 452: Pending outbound cctx, originating from ZetaChain. Additionally, in lines `453`, `463`, and `476`, the coin type is checked to determine the specific type of transaction.
3. Line 491: Revert a failed cctx that was originally sent to ZetaChain
4. Line 515: Revert a failed cctx that was originally sent to an external chain
5. Line 530: Pending outbound cctx. No matter the coin type, it will always result in a Zeta token transfer

In the second state, in line [`452`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L452), it is also checked if outbound transactions are generally enabled (`flags.IsOutboundEnabled`) and if they are disabled, this `else if` block is skipped while the `if` in line [`530`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L530) evaluates to `true`.

However, this is problematic in two ways:

1. Even though outbound transactions are disabled, cctxs are still sent out.
2. No matter the coin type of the pending outbound cctx, it will be signed via `SignOutboundTx` and resulting in a Zeta token transfer

For the second case, consider a pending outbound cctx with the coin type `common.CoinType_ERC20` where the ERC-20 `asset` is worth less than the Zeta token (please note that [ERC-20 tokens are restricted by a whitelist](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174-L176)).

As a result of this issue, the recipient of the cctx receives Zeta tokens instead of the lower-valued ERC-20 tokens, effectively stealing Zeta tokens for profit. Moreover, if users attempt to withdraw gas or ERC-20 tokens that have a higher value than the Zeta token, users will receive a total value Zeta tokens less than their original gas/ERC-20 tokens, resulting in a loss.

## Tools Used

Manual review

## Recommended mitigation steps

Consider refactoring the control flow by first checking if outbound transactions are enabled (the `CoinType_Cmd` cctx can be exempted from this check), and only then continue with the other checks.



## Assessed type

Invalid Validation
