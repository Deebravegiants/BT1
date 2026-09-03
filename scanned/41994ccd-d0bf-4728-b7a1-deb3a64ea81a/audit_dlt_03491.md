# [H] zEVM cross-chain messages ignore the user-specified message and prevent calling the destination contract

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/413
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L221


# Vulnerability details

## Impact

Cross-chain Zeta messages originating from the zEVM have an empty `message` field, preventing the `destinationAddress` contract from being called.

This renders the cross-chain messaging functionality useless as the `message` is never used and potentially causes a loss of funds (if assets have been burned on the zEVM) or locked funds (if unable to unlock on the receiver end).

## Proof of Concept

zEVM transactions are post-processed in the [`PostTxProcessing`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L42-L44) function of the `x/crosschain` module. Specifically, the goal is to parse and process `ZetaSent` and ZRC-20 `Withdrawal` events and send them to the corresponding, external receiver chains.

Any emitted `ZetaSent` events are parsed and processed in the [`ProcessZetaSentEvent`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L172-L246) function. This event is emitted by the [`ZetaConnectorZEVM.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92-L108) function to send a cross-chain message to an external chain.

The message input, [`ZetaInterfaces.SendInput`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L8-L21), allows the sender to specify a `message` that is forwarded to the receiver contract (`destinationAddress`) on the destination chain.

Specifically, once the cross-chain message is received by the `onReceive` function of the ZetaConnector contract on the receiver chain (e.g., [`ZetaConnectorEth`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) or [`ZetaConnectorNonEth`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)), the [`destinationAddress`'s `onZetaMessage` function is called](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L64-L66) and the `message` is provided as a parameter.

However, the user-specified `message` is not used, instead, it is [overwritten by an empty string in line 221](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L221).

```go
172: func (k Keeper) ProcessZetaSentEvent(ctx sdk.Context, event *connectorzevm.ZetaConnectorZEVMZetaSent, emittingContract ethcommon.Address, txOrigin string) error {
...  	// [...]
212:
213: 	// Bump gasLimit by event index (which is very unlikely to be larger than 1000) to always have different ZetaSent events msgs.
214: 	msg := types.NewMsgVoteOnObservedInboundTx(
215: 		"",
216: 		emittingContract.Hex(),
217: 		senderChain.ChainId,
218: 		txOrigin, toAddr,
219: 		receiverChain.ChainId, /
220: 		amount,
221: ❌		"",
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/413_
