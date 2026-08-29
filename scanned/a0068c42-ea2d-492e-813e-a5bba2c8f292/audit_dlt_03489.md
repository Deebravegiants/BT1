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


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/416_
