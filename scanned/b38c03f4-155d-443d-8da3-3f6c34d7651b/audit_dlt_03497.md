# [H] Inconsistent Voting Index Leads to Double Spends in Future

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-15
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/327
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/proto/crosschain/tx.proto#L141
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/proto/crosschain/tx.proto#L117


# Vulnerability details

## Impact
The voting process works as follows: 

1. An observer sees an event and sends a message to Zetachain to vote on the occurrence. 
2. The message structure is hashed to determine the ballot to be used.
3. The vote is added based upon the hashed value. 
4. If enough votes have been received, then the finalization occurs. This means relaying to the zEVM or another chain. 
  
The ``index`` of an observed transaction ``MsgVoteOnObservedInboundTx`` is calculated by taking a *hash* of the incoming message. For every observer that votes on a given event, the index should be the same. The protection in place for stopping *duplicate* transactions is simply checking if this ``index`` has occurred already. Since the ballots are never deleted, this works well. 
  
However, the ``index`` is *too granular*. Many aspects of an event are guaranteed to not change: sender/receiver change, tx hash, amount, cointype, etc. This is NOT the case with several of the fields that are hardcoded into the Zetaclient but may change in the future. Gaslimit (hardcoded in app) and asset (which is currently blank) are unused fields that may change in the future. On top of this, a change in encoding, what the zetaclient signs or anything else would result in a different hash as well.
  
Additionally, any newly added fields would change the index of previous ballots as well. If this sounds farfetched, there is already a case of this happening since deployment. The field ``eventIndex`` was added very recently to the repository, since multiple events can happen within a single transaction. If the current Zetachain deployment had the ``AddToInTxTracker`` then it would be possible to exploit the new ``eventIndex`` field changes the hash to retrigger the CCTX.
  
If any of these values change in the future, then the ballot ``index`` would change. Since this index is the only security protection for duplicate submissions, the same event could be submitted once again. To make matters worse, there is nothing within the ``TxInTracker`` on the zetachain or zetaclient that checks that an event has already occurred. This allows for trivial exploitation when the client or parts of the message are updated.
  
Relying on this index to never change is an unspoken variant now. Since this is not mentioned anywhere, a tiny change made by a developer would result in every CCTX previously created to be valid in the voting process once again. Although there is some waiting involved, a malicious adversary could send CCTXs and simply wait for them to be valid again once a change to the Zetachain or Zetaclient is made.

Attack strategy:

1. Transfer BTC, ETH, ERC20 and Zeta between several different chains in large quantities. 
2. Wait for a change in one of the above fields to occur within the Zetaclient.
3. Resubmit an old transaction into the ``TxInTracker`` with a proof. The zetaclient will see this and all observers will vote on the event occurrence. 
4. Massive profit from duplicate event submission. This can only be done once for very change on the fields. With enough sending of funds back and forth prior to the update, this could lead to massive profits for an attacker.


## Proof of Concept

This proof of concept demonstrates the issue from the Cosmos SDK tests. It sends two events that only differ by the ``GasLimit`` and checks if they get approved or not. To make the proof of concept more viable, you could simulate a change on the zetaclient parameters and send a proof through the ``TxInTracker`` afterwards. Since this requires a change to the zetaclient live, we felt that a Cosmos SDK PoC was clearer to reproduce and easier to understand.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/327_
