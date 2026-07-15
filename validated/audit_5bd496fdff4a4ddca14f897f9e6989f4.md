Let me look at the `transaction_ack` handler and the `_retry_fee_failed_transactions` function more carefully.

### Title
Malicious Full Node Can Permanently Suppress Transaction Failure via Crafted `INVALID_FEE_LOW_FEE` TransactionAck — (`chia/wallet/transaction_record.py`, `chia/wallet/wallet_node_api.py`)

---

### Summary

`TransactionRecordOld.is_valid()` treats any `sent_to` entry whose error string matches `Err.INVALID_FEE_LOW_FEE.name` or `Err.INVALID_FEE_TOO_CLOSE_TO_ZERO.name` as a temporary, retryable failure — regardless of how many other peers have permanently rejected the transaction. A malicious full node that the wallet has legitimately sent a spend bundle to can exploit this by returning a crafted `TransactionAck(status=FAILED, error='INVALID_FEE_LOW_FEE')`. Because the check uses `any()` over the entire `sent_to` list and does not cross-validate the status field, a single poisoned entry keeps `is_valid()` returning `True` forever, preventing the wallet from ever marking the transaction as permanently failed.

---

### Finding Description

**Step 1 — Entrypoint: `transaction_ack` handler**

The wallet's `WalletNodeAPI.transaction_ack` handler processes acks from connected full nodes. [1](#0-0) 

A guard (`matched_in_flight_send`) at lines 110–123 rejects unsolicited acks — it requires `ack.txid` to appear in `_tx_messages_in_progress[peer.peer_node_id]`. This is satisfied whenever the wallet has already sent a `SendTransaction` to that peer, which happens automatically for every connected full node. [2](#0-1) 

**Step 2 — Unvalidated error string forwarded verbatim**

At line 146, `ack.error` is used directly as a key into the `Err` enum with no validation that the error is consistent with the status code:

```python
await wallet_state_manager.remove_from_queue(ack.txid, name, status, Err[ack.error])
``` [3](#0-2) 

**Step 3 — `increment_sent` stores the poisoned entry**

`remove_from_queue` calls `increment_sent`, which stores `(peer_name, uint8(FAILED), 'INVALID_FEE_LOW_FEE')` into `sent_to` and then calls `tx.is_valid()` to decide whether to mark the transaction as permanently failed. [4](#0-3) 

**Step 4 — The logic flaw in `is_valid()`**

```python
if any(x[2] in {Err.INVALID_FEE_LOW_FEE.name, Err.INVALID_FEE_TOO_CLOSE_TO_ZERO.name} for x in self.sent_to):
    return True
``` [5](#0-4) 

This check:
- Inspects only `x[2]` (the error string), **never** `x[1]` (the `MempoolInclusionStatus` value)
- Uses `any()`, so **one** poisoned entry in `sent_to` overrides any number of legitimate permanent-failure entries (e.g., `DOUBLE_SPEND`, `ASSERT_COIN_CONSUMED_FAILED`)

Because `is_valid()` returns `True`, the `if not tx.is_valid()` branch in `increment_sent` is never taken, and the transaction is never marked `confirmed=True` at height 0 (the "failed" sentinel). [6](#0-5) 

**Step 5 — Indefinite retry loop**

The wallet's `_retry_fee_failed_transactions` path is designed to re-send fee-rejected transactions. With `is_valid()` permanently returning `True`, the transaction stays unconfirmed, is re-queued, and the malicious peer can keep responding with `INVALID_FEE_LOW_FEE` indefinitely.

---

### Impact Explanation

The wallet never transitions the transaction to a terminal failed state. The spend bundle's removal coins remain "in flight" in the wallet's internal accounting. The user cannot determine that the transaction is permanently invalid, cannot reclaim the coins for a replacement transaction, and the wallet wastes resources retrying forever. This is a **long-lived inability for an honest wallet to process spend bundles** caused by a single malicious peer.

---

### Likelihood Explanation

Any full node the wallet connects to (including nodes discovered via the peer exchange) can execute this attack. The wallet connects to untrusted peers by default. The attacker only needs to:
1. Accept the wallet's `SendTransaction` (satisfying the `matched_in_flight_send` guard)
2. Reply with a crafted `TransactionAck`

No key material, admin access, or cryptographic break is required.

---

### Recommendation

Fix `is_valid()` to require that the fee-error entry also carries `MempoolInclusionStatus.FAILED` **and** that no other entry carries a non-fee permanent error for the same peer. At minimum, change the fee-error branch to also verify `x[1] == MempoolInclusionStatus.FAILED.value`:

```python
if any(
    x[1] == MempoolInclusionStatus.FAILED.value
    and x[2] in {Err.INVALID_FEE_LOW_FEE.name, Err.INVALID_FEE_TOO_CLOSE_TO_ZERO.name}
    for x in self.sent_to
):
    return True
```

Additionally, consider capping the number of fee-retry attempts or adding a wall-clock deadline after which a fee-failed transaction is also marked permanently invalid.

---

### Proof of Concept

```python
# 1. Wallet creates a tx spending coin C (already spent on-chain).
# 2. Wallet connects to attacker's full node; sends SendTransaction(sb).
# 3. Attacker's node receives sb, computes txid = sb.name().
# 4. Attacker sends:
#      TransactionAck(txid=txid, status=FAILED, error='INVALID_FEE_LOW_FEE')
#    This satisfies matched_in_flight_send (txid was in _tx_messages_in_progress).
# 5. wallet_node_api calls remove_from_queue(txid, peer_name, FAILED, Err.INVALID_FEE_LOW_FEE)
# 6. increment_sent appends (peer_name, uint8(3), 'INVALID_FEE_LOW_FEE') to sent_to.
# 7. is_valid() → any(x[2] in {'INVALID_FEE_LOW_FEE',...}) → True
# 8. Transaction NOT marked confirmed=True; stays unconfirmed forever.
# 9. Honest peers reject with DOUBLE_SPEND, but any() means the fee entry wins.
# 10. _retry_fee_failed_transactions keeps re-sending; attacker keeps replying.
# Assert: tx.is_valid() == True after N rounds for any N.
# Assert: tx.confirmed == False indefinitely.
# Assert: coin C is never freed in wallet state.
```

### Citations

**File:** chia/wallet/wallet_node_api.py (L100-148)
```python
    @metadata.request(peer_required=True)
    async def transaction_ack(self, ack: wallet_protocol.TransactionAck, peer: WSChiaConnection) -> None:
        """
        This is an ack for our previous SendTransaction call. This removes the transaction from
        the send queue if we have sent it to enough nodes.
        """
        async with self.wallet_node.wallet_state_manager.lock:
            assert peer.peer_node_id is not None
            name = peer.peer_node_id.hex()
            matched_in_flight_send = False
            if peer.peer_node_id in self.wallet_node._tx_messages_in_progress:
                in_progress = self.wallet_node._tx_messages_in_progress[peer.peer_node_id]
                if ack.txid in in_progress:
                    matched_in_flight_send = True
                    in_progress.remove(ack.txid)
                if in_progress == []:
                    del self.wallet_node._tx_messages_in_progress[peer.peer_node_id]

            # Ignore stale/unsolicited acknowledgements that don't correspond to an in-flight send.
            if not matched_in_flight_send:
                self.wallet_node.log.debug(
                    "Ignoring unsolicited transaction ack from peer %s for tx %s", name, ack.txid
                )
                return

            status = MempoolInclusionStatus(ack.status)
            try:
                wallet_state_manager = self.wallet_node.wallet_state_manager
            except RuntimeError as e:
                if "not assigned" in str(e):
                    return
                raise

            if status == MempoolInclusionStatus.SUCCESS:
                self.wallet_node.log.info(
                    f"SpendBundle has been received and accepted to mempool by the FullNode. {ack}"
                )
            elif status == MempoolInclusionStatus.PENDING:
                self.wallet_node.log.info(f"SpendBundle has been received (and is pending) by the FullNode. {ack}")
            else:
                if not self.wallet_node.is_trusted(peer) and ack.error == Err.NO_TRANSACTIONS_WHILE_SYNCING.name:
                    self.wallet_node.log.info(f"Peer {peer.get_peer_info()} is not synced, closing connection")
                    await peer.close()
                    return
                self.wallet_node.log.warning(f"SpendBundle has been rejected by the FullNode. {ack}")
            if ack.error is not None:
                await wallet_state_manager.remove_from_queue(ack.txid, name, status, Err[ack.error])
            else:
                await wallet_state_manager.remove_from_queue(ack.txid, name, status, None)
```

**File:** chia/wallet/wallet_transaction_store.py (L191-209)
```python
        err_str = err.name if err is not None else None
        append_data = (name, uint8(send_status.value), err_str)

        for peer_id, status, error in sent_to:
            current_peers.add(peer_id)

        if name in current_peers:
            sent_count = uint32(current.sent)
        else:
            sent_count = uint32(current.sent + 1)

        sent_to.append(append_data)

        tx: TransactionRecord = dataclasses.replace(current, sent=sent_count, sent_to=sent_to)
        if not tx.is_valid():
            # if the tx is not valid due to repeated failures, we will confirm that we can't spend it
            log.info(f"Marking tx={tx.name} as confirmed but failed, since it is not spendable due to errors")
            tx = dataclasses.replace(tx, confirmed=True, confirmed_at_height=uint32(0))
        await self.add_transaction_record(tx)
```

**File:** chia/wallet/transaction_record.py (L89-91)
```python
        if any(x[2] in {Err.INVALID_FEE_LOW_FEE.name, Err.INVALID_FEE_TOO_CLOSE_TO_ZERO.name} for x in self.sent_to):
            # we tried to push it to mempool and got a fee error so it's a temporary error
            return True
```
