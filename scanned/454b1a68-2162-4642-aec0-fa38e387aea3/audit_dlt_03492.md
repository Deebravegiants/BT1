# [H] Outbound transactions that can not be broadcasted to an external EVM chain cause a Denial of Service of all outgoing transactions to this chain

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/412
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L579


# Vulnerability details

## Impact

Outgoing transactions to an external EVM chain can be maliciously blocked by crafting a cctx that can not be broadcasted, i.e., causing the RPC to error (with an error that is not handled in the `HandleBroadcastError` function).

For example, causing the intrinsic gas limit to exceed the provided gas limit (minimum `100k`) prevents the transaction from being included in the EVM mempool and blocks the queue of pending outgoing transactions to this external chain.

This is non-recoverable and requires manual intervention and coordination of all validators (observers) to fix the blocking nonce.

## Proof of Concept

Observers retry failed outbound transaction broadcasts for a maximum of 5 retries. Subsequently, in the last retry attempt, the `for` loop is exited in line [`579`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L579) and the function execution is finished.

_Please note that the [`HandleBroadcastError`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L335-L350) function in line `570` only handles certain RPC errors and otherwise, simply instructs a retry._

On the next ticker, the `TryProcessOutTx` function attempts to send this cctx again but continues to fail. As nonces on the external chain have to be sequential without gaps, any other transactions are blocked from being sent to this external chain.

```go
562:// retry loop: 1s, 2s, 4s, 8s, 16s in case of RPC error
563:for i := 0; i < 5; i++ {
564:	logger.Info().Msgf("broadcasting tx %s to chain %s: nonce %d, retry %d", outTxHash, toChain, send.GetCurrentOutTxParam().OutboundTxTssNonce, i)
565:	// #nosec G404 randomness is not a security issue here
566:	time.Sleep(time.Duration(rand.Intn(1500)) * time.Millisecond) // FIXME: use backoff
567:	err := signer.Broadcast(tx)
568:	if err != nil {
569:		log.Warn().Err(err).Msgf("OutTx Broadcast error")
570:		retry, report := HandleBroadcastError(err, strconv.FormatUint(send.GetCurrentOutTxParam().OutboundTxTssNonce, 10), toChain.String(), outTxHash)
571:		if report {
572:			zetaHash, err := zetaBridge.AddTxHashToOutTxTracker(toChain.ChainId, tx.Nonce(), outTxHash, nil, "", -1)
573:			if err != nil {
574:				logger.Err(err).Msgf("Unable to add to tracker on ZetaCore: nonce %d chain %s outTxHash %s", send.GetCurrentOutTxParam().OutboundTxTssNonce, toChain, outTxHash)
575:			}
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/412_
