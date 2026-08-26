# [H] Fake `ZetaReceived` events cause the outbound cctx to remain pending resulting in a blocked outbound EVM transaction queue

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/418
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L386
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L423
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L181-L185


# Vulnerability details

## Impact

Events such as `ZetaReceived` or `ZetaReverted`, supposed to be emitted by the connector contract, can be faked by the receiver contract that is called as part of the [`onReceive`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L64-L66) or [`onRevert`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L90-L99) call.

Worst case, a cctx can be purposefully caused to remain stuck in the `PendingOutbound` state, which blocks the outbound EVM transaction queue and prevents further outbound transactions from being sent.

## Proof of Concept

The observer's EVM client confirms sent outbound transaction within the [`IsSendOutTxProcessed`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L295) function and sends the confirmation (i.e., `MsgVoteOnObservedOutboundTx` vote message) to ZetaChain to ultimately finalize and settle the cctx.

Specifically, outbound cctx's of type `CoinType_Zeta` are processed by checking the emitted events (logs) of the containing transaction. It is expected that either the `ZetaReceived` or `ZetaReverted` event is **emitted by the connector contract**.

However, in line [`386`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L386) (and following), the event's legitimacy is not verified by checking the emitter contract address.

```go
386: 	receivedLog, err := connector.ZetaConnectorNonEthFilterer.ParseZetaReceived(*vLog)
```

Internally, the [`ParseZetaReceived`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/pkg/contracts/evm/zetaconnector.non-eth.sol/zetaconnectornoneth.go#L1587-L1594) function only parses the event and makes sure the event's signature matches the expected one.

```go
func (_ZetaConnectorNonEth *ZetaConnectorNonEthFilterer) ParseZetaReceived(log types.Log) (*ZetaConnectorNonEthZetaReceived, error) {
	event := new(ZetaConnectorNonEthZetaReceived)
	if err := _ZetaConnectorNonEth.contract.UnpackLog(event, "ZetaReceived", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/418_
