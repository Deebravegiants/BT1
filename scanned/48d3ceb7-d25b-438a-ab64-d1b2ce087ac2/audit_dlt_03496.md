# [H] Outbound Confirmation Tracker Race Condition Leads to a Double Spend

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-15
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/338
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L610
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L295


# Vulnerability details

## Impact
In the Zellic audit, the report ``3.2 Bonded validators can trigger reverts for successful transactions`` points out that the ``RemoveFromOutTxTracker`` can be called by any bonded validator. They mention this as being an issue then mention an exploit path to use, which is the focus of that finding. The ``RemoveFromOutTxTracker`` issue resulting from bad access control issue was remediated, however there is another way to use the same exploit.
  
Their method of exploitation is as follows: 

1. Create a CCTX from one EVM chain to a different EVM chain, transferring ZETA
2. Process the incoming event so that it's put into the ``PendingOutbound`` state. 
3. The zetaclient signs the transaction with the ``TryProcessOutTx`` then broadcasts this to the EVM. Right after the voting, the zetaclient will also add the transaction to the ``OutboundTxTracker``. 
4. Call ``RemoveFromOutTxTracker`` to remove the outbound transaction so that the Zetaclient will never see it. While this exact method is fixed, we can replicate the *removal* with a race condition that will be described below.
5. Call ``AddToOutTxTracker`` where the same nonce as the transaction from the TSS address. Make this a reverted transaction so that we trick the processing to eventually call ``onRevert``. 
6. ``observeTxOut`` picks up the FAKE transaction as being reverted, even though it actually succeeded. This will put the tx into the ``ob.outTXConfirmationTransaction`` and ``ob.outTXConfirmationReceipts`` structure. 
7. With the transactions and receipt in the structures, another thread calls ``PostReceiveConfirmation`` on our fake transaction as being reverted. After enough of these, a vote passes that validates that the transaction did in fact fail.
8. The revert flow will occur. This will send us back the funds on the EVM chain even though they were already sent once in the original transaction.
  
By adding a reverted transaction to the ``OutTxTracker`` at just the right moment, it is possible to cause a **race condition** where the real transaction is broadcasted to the outbound chain but the wrong tx is processed through the queue for the ``OutTracker``. This is able to replicate the effect of step 4 of the Zellic method, since we can get our fake transaction processed *first* in the voting process. The timing for performing a double spend is very tight though. In particular, the function must be within the *signing* process of our CCTX but has NOT added the TX to the outbound queue yet when we add the function to the ``OutTxTracker``. If this is done, a double spend will occur. However, causing a denial of service by sending the fake transaction as soon as possible is trivial. We were able to replicate the double spend a few times but got the denial of service every time. The double spend has a [video](https://www.youtube.com/watch?v=i360xH6ex_4) below since it is hard to trigger.
  
The real issue stems from the items going into the ``ob.outTXConfirmationTransaction`` and ``ob.outTXConfirmationReceipts`` structure without the *events* ever being validated properly. Additionally, only the *first* item within a given ``OutTxTracker`` is ever used. The only item that is validated on the processing is that the *nonce* of the transaction matches the nonce of the TSS CCTX. However, this is trivial to bypass using a different key.
  
Another interesting point is *who* can trigger the vulnerability. For testing, we mostly used an observer because we never got the *proof* functionality working. To our understanding, this provides three checks: 
* The ``To()`` must be to the connector address.
* The block header for the TX must be uploaded. This means that the confirmation point must be reached. 
* The TX must be valid and occurred. 

All of these are trivial to bypass. First, we simply send a transaction to the ``connector`` that fails for whatever reason, which satisfies part 1. Part 2 can be bypassed by simply waiting for enough blocks on our fake transaction. Part 3 can be bypassed by using a valid proof, which should be easy to do. 

All of this together means that any user can exploit the double spend but it's much easier for observers to do, since no proof is required. This was only tested on Ethereum but may also work on Bitcoin as well. This vulnerability is live on the existing system.

## Proof of Concept 
### Setup
The setup for exploitation on this is complicated within the test environment. Messing up a single step will make this not work. If there is difficultly in reproducing, please reach out and we can demonstrate it. Here is a [video](https://www.youtube.com/watch?v=i360xH6ex_4) of the exploit occurring as well.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/338_
