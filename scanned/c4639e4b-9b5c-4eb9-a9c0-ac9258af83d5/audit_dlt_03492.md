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
576:			logger.Info().Msgf("Broadcast to core successful %s", zetaHash)
577:		}
578:		if !retry {
579:			break
580:		}
581:		backOff *= 2
582:		continue
583:	}
584:	logger.Info().Msgf("Broadcast success: nonce %d to chain %s outTxHash %s", send.GetCurrentOutTxParam().OutboundTxTssNonce, toChain, outTxHash)
585:	zetaHash, err := zetaBridge.AddTxHashToOutTxTracker(toChain.ChainId, tx.Nonce(), outTxHash, nil, "", -1)
586:	if err != nil {
587:		logger.Err(err).Msgf("Unable to add to tracker on ZetaCore: nonce %d chain %s outTxHash %s", send.GetCurrentOutTxParam().OutboundTxTssNonce, toChain, outTxHash)
588:	}
589:	logger.Info().Msgf("Broadcast to core successful %s", zetaHash)
590:	break // successful broadcast; no need to retry
591:}
```

### How to exploit

[The EVM validates the incoming transaction to exclude transactions with basic errors, such as insufficient intrinsic gas](https://github.com/ethereum/go-ethereum/blob/69576df2544d9a6c59c5659b82a064edc9845874/core/txpool/legacypool/legacypool.go#L977-L984), before being put into the mempool.

In regards to the intrinsic gas, a single non-zero byte of transaction data [costs 16 gas](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/params/protocol_params.go#L93), plus an additional [flat fee of `21_000`](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/params/protocol_params.go#L36). For more details on how the intrinsic gas is calculated, see the EVM's [`IntrinsicGas` function](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/core/state_transition.go#L69-L116).

[If the transaction's gas limit is insufficient to cover the intrinsic gas, the transaction will be rejected, and the RPC call will result in an error.](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/core/txpool/validation.go#L99-L105)

This fact can be exploited, e.g., by sending a Zeta cross-chain message from an external chain A to chain B via the [`ZetaConnectorEth.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L45) function. Specifically, an attacker can provide a message, `input.message`, with a length that ultimately exceeds the maximum message limit of [`MaxMessageLength = 10240`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L15) (this [maximum length is enforced in the `MsgVoteOnObservedInboundTx` message's `ValidateBasic` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L88-L90) and [prevents observers from sending such a message to ZetaChain](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/tx.go#L74) as well as also preventing any further processing of the message in case it reaches ZetaChain).

As the maximum message length is not exceeded, the inbound transaction is sent to ZetaChain, and once it's successfully voted upon, the resulting cctx is put into the pending queue of outgoing transactions.

Subsequently, observers will [process the cctx](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L143) and attempt to send the transaction to the external chain B by collectively signing and [broadcasting the message to the chain](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L567).

Given that the provided message and its length is `7680` (please refer to the [PoC](#simple-poc) below for details on how this value is chosen), the intrinsic gas cost is `7680 * 16 = 122880 + flat fee of 21k = ~144k` and the transaction **must** have at least this amount of gas to be accepted by the RPC.

However, sending Zeta messages allows [specifying](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L41) an arbitrary (non-zero) destination gas limit, which is [lower-bounded to `100_000`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L375-L378).

Consequently, the gas limit can be forced to be set to `100k`. Attempting to broadcast such a transaction to the EVM RPC will result in an error due to the validation of the intrinsic gas costs of `~144k` and the insufficient provided gas of `100k`.

### Simple PoC

The following Solidity contract demonstrates how such a cross-chain message with the maximum message length of `10240` can be crafted:

[Internally, the observer encodes the message to base64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/utils.go#L165), thus increasing the length of the message by roughly a [factor of 4/3](https://en.wikipedia.org/wiki/Base64). Consequently, to not exceed the maximum message length, the message length is set to `10240 * 3/4 = 7680` in Solidity.

```solidity
contract ZetaChain is ZetaReceiver {
    ZetaConnector public connector = ZetaConnector(0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9);
    IERC20 public zeta = IERC20(0xA8D5060feb6B456e886F023709A2795373691E63);

    function send(uint256 amount, uint256 gasLimit) external {
        uint256 length = 7680;

        bytes memory message = new bytes(length);
        // fill with non-zero data
        for (uint256 i = 0; i < length; i++) {
            message[i] = bytes1(uint8(1));
        }

        ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
            1337,
            abi.encodePacked(address(this)),
            gasLimit,
            message,
            amount,
            ""
        );

        zeta.transferFrom(msg.sender, address(this), amount);
        zeta.approve(address(connector), amount);

        connector.send(input);
    }
}
```

Calling this `send` function on the custom deployed `ZetaChain` contract on Ethereum, with `amount = 4e18` and `gasLimit = 100_000`, causes the `ZetaSent` event to be emitted and picked up by the observers.

Once the transaction is sent to ZetaChain and finalized, observers attempt to broadcast the transaction to the receiver chain but fail with the following RPC error:

```bash
ERR Broadcast error: nonce 3 chain chain_name:goerli_localnet chain_id:1337  outTxHash 0x749c4e60f0428ba4f558bfca892dca5ba70bc9542e26f1f978240eaf0d5d73fe; retrying... error="intrinsic gas too low"
```

## Tools Used

Manual review

## Recommended mitigation steps

Consider properly handling a repeatedly failed RPC call in the `TryProcessOutTx` function and ensure that such a blocked (pending) nonce can be fixed, i.e., assigned to another cctx that can be broadcasted.

Additionally, consider lowering the maximum message length or adjusting the minimum gas limit to ensure the intrinsic gas costs are covered.



## Assessed type

Other
