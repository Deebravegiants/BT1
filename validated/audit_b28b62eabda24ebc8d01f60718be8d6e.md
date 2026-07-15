### Title
Missing `header_hash` Binding Check in `request_validate_wp` Allows Malicious Peer to Redirect Full Node Sync to an Alternative Chain — (`File: chia/full_node/full_node.py`)

---

### Summary

`FullNode.request_validate_wp()` validates a weight proof returned by a peer by checking only `height` and `weight`, but never verifies that the proof's tip `header_hash` matches the `peak_header_hash` that was originally requested. A malicious peer can return a cryptographically valid weight proof for a different fork with the same height and weight, causing the victim full node to sync to that alternative chain. The wallet's equivalent function (`fetch_and_update_weight_proof`) performs all three checks and is not affected.

---

### Finding Description

During long sync, `FullNode._sync()` selects the heaviest announced peak and calls `request_validate_wp(target_peak.header_hash, target_peak.height, target_peak.weight)`. [1](#0-0) 

Inside `request_validate_wp`, after receiving the weight proof from the peer, only two fields are checked:

```python
if response.wp.recent_chain_data[-1].reward_chain_block.height != peak_height:
    ...
if response.wp.recent_chain_data[-1].reward_chain_block.weight != peak_weight:
    ...
``` [2](#0-1) 

The `header_hash` of the proof's tip is **never compared** to `peak_header_hash`. The weight proof then passes into `validate_weight_proof`, which performs cryptographic VDF and sub-epoch validation but also does not bind the proof to a specific tip hash. [3](#0-2) 

By contrast, the wallet's `fetch_and_update_weight_proof` performs all three checks explicitly:

```python
if weight_proof.recent_chain_data[-1].height != peak.height:
    raise Exception("weight proof height does not match peak")
if weight_proof.recent_chain_data[-1].weight != peak.weight:
    raise Exception("weight proof weight does not match peak")
if weight_proof.recent_chain_data[-1].header_hash != peak.header_hash:
    raise Exception("weight proof peak hash does not match peak")
``` [4](#0-3) 

The missing check is the direct analog of the external report's missing `yaru.adapters()` check: both functions verify some attributes of the source (height + weight / sender + chainId) but omit the binding attribute that ties the response to the specific requested identity (header_hash / oracle list).

---

### Impact Explanation

After `request_validate_wp` returns, the full node immediately calls `sync_from_fork_point` using the fork point and summaries derived from the attacker-supplied proof, then downloads and applies blocks from peers that have the *attacker's* chain. [5](#0-4) 

If the attacker's chain is accepted, the full node diverges from the canonical network chain. This is **consensus divergence** caused by a protocol-level sync path interaction, matching the Critical impact class.

---

### Likelihood Explanation

The attacker must:
1. Possess a valid alternative Chia chain with the same height and weight as the main chain (requires significant proof-of-space resources or a deep historical fork).
2. Announce the main chain's `peak_header_hash` to the victim so they appear in `peers_with_peak`.
3. When queried for a weight proof, return a valid proof for their own fork.

The weight proof validation (`_validate_sub_epoch_summaries`, VDF checks, `validate_recent_blocks`) is thorough and requires a genuinely valid chain — the attacker cannot fabricate data from nothing. This raises the bar significantly. However, the missing check is a structural gap that the wallet already closes, confirming it is a known necessary guard.

---

### Recommendation

Add the missing `header_hash` binding check immediately after the existing height and weight checks in `request_validate_wp`, mirroring the wallet's implementation:

```python
if response.wp.recent_chain_data[-1].header_hash != peak_header_hash:
    await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
    raise RuntimeError(
        f"Weight proof tip hash mismatch: {weight_proof_peer.peer_info.host}"
    )
``` [2](#0-1) 

---

### Proof of Concept

1. Attacker operates a full node on a valid minority fork with the same height and weight as the main chain.
2. Attacker connects to the victim full node and announces the main chain's `NewPeak` (same `header_hash`, `height`, `weight`), causing the victim to add the attacker to `peers_with_peak` for that hash.
3. Victim enters long sync and calls `request_validate_wp(main_peak_header_hash, height, weight)`.
4. Attacker is randomly selected from `peers_with_peak` and returns `RespondProofOfWeight` containing a valid weight proof for the attacker's fork (different `header_hash`, same `height` and `weight`).
5. `request_validate_wp` checks `height` ✓ and `weight` ✓ but skips `header_hash` — no rejection occurs.
6. `validate_weight_proof` passes (the attacker's chain is cryptographically valid).
7. `sync_from_fork_point` downloads and applies the attacker's chain blocks; the victim full node diverges from the canonical network. [6](#0-5) [7](#0-6)

### Citations

**File:** chia/full_node/full_node.py (L1116-1118)
```python
            fork_point, summaries = await self.request_validate_wp(
                target_peak.header_hash, target_peak.height, target_peak.weight
            )
```

**File:** chia/full_node/full_node.py (L1120-1128)
```python
            async with self.blockchain.priority_mutex.acquire(priority=BlockchainMutexPriority.high):
                await self.blockchain.warmup(fork_point)
                fork_point = await check_fork_next_block(
                    self.blockchain,
                    fork_point,
                    self.get_peers_with_peak(target_peak.header_hash),
                    node_next_block_check,
                )
                await self.sync_from_fork_point(fork_point, target_peak.height, target_peak.header_hash, summaries)
```

**File:** chia/full_node/full_node.py (L1138-1194)
```python
    async def request_validate_wp(
        self, peak_header_hash: bytes32, peak_height: uint32, peak_weight: uint128
    ) -> tuple[uint32, list[SubEpochSummary]]:
        if self.weight_proof_handler is None:
            raise RuntimeError("Weight proof handler is None")
        peers_with_peak = self.get_peers_with_peak(peak_header_hash)
        # Request weight proof from a random peer
        peers_with_peak_len = len(peers_with_peak)
        self.log.info(f"Total of {peers_with_peak_len} peers with peak {peak_height}")
        # We can't choose from an empty sequence
        if peers_with_peak_len == 0:
            raise RuntimeError(f"Not performing sync, no peers with peak {peak_height}")
        weight_proof_peer: WSChiaConnection = random.choice(peers_with_peak)
        self.log.info(
            f"Requesting weight proof from peer {weight_proof_peer.peer_info.host} up to height {peak_height}"
        )
        cur_peak: BlockRecord | None = self.blockchain.get_peak()
        if cur_peak is not None and peak_weight <= cur_peak.weight:
            raise ValueError("Not performing sync, already caught up.")
        wp_timeout = 360
        if "weight_proof_timeout" in self.config:
            wp_timeout = self.config["weight_proof_timeout"]
        self.log.debug(f"weight proof timeout is {wp_timeout} sec")
        request = full_node_protocol.RequestProofOfWeight(peak_height, peak_header_hash)
        response = await weight_proof_peer.call_api(FullNodeAPI.request_proof_of_weight, request, timeout=wp_timeout)
        # Disconnect from this peer, because they have not behaved properly
        if response is None or not isinstance(response, full_node_protocol.RespondProofOfWeight):
            await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
            raise RuntimeError(f"Weight proof did not arrive in time from peer: {weight_proof_peer.peer_info.host}")
        if response.wp.recent_chain_data[-1].reward_chain_block.height != peak_height:
            await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
            raise RuntimeError(f"Weight proof had the wrong height: {weight_proof_peer.peer_info.host}")
        if response.wp.recent_chain_data[-1].reward_chain_block.weight != peak_weight:
            await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
            raise RuntimeError(f"Weight proof had the wrong weight: {weight_proof_peer.peer_info.host}")
        if self.in_bad_peak_cache(response.wp):
            raise ValueError("Weight proof failed bad peak cache validation")
        # dont sync to wp if local peak is heavier,
        # dont ban peer, we asked for this peak
        current_peak = self.blockchain.get_peak()
        if current_peak is not None:
            if response.wp.recent_chain_data[-1].reward_chain_block.weight <= current_peak.weight:
                raise RuntimeError(
                    f"current peak is heavier than Weight proof peek: {weight_proof_peer.peer_info.host}"
                )
        try:
            validated, fork_point, summaries = await self.weight_proof_handler.validate_weight_proof(response.wp)
        except Exception as e:
            await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
            raise ValueError(f"Weight proof validation threw an error {e}")
        if not validated:
            await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
            raise ValueError("Weight proof validation failed")
        self.log.info(f"Re-checked peers: total of {len(peers_with_peak)} peers with peak {peak_height}")
        self.sync_store.set_sync_mode(True)
        self._state_changed("sync_mode")
        return fork_point, summaries
```

**File:** chia/wallet/wallet_node.py (L1463-1488)
```python
    async def fetch_and_update_weight_proof(self, peer: WSChiaConnection, peak: HeaderBlock) -> int:
        assert self._weight_proof_handler is not None
        weight_request = RequestProofOfWeight(peak.height, peak.header_hash)
        wp_timeout = self.config.get("weight_proof_timeout", 360)
        self.log.debug(f"weight proof timeout is {wp_timeout} sec")
        weight_proof_response: RespondProofOfWeight = await peer.call_api(
            FullNodeAPI.request_proof_of_weight, weight_request, timeout=wp_timeout
        )

        if weight_proof_response is None:
            raise Exception("weight proof response was none")

        weight_proof = weight_proof_response.wp

        if weight_proof.recent_chain_data[-1].height != peak.height:
            raise Exception("weight proof height does not match peak")
        if weight_proof.recent_chain_data[-1].weight != peak.weight:
            raise Exception("weight proof weight does not match peak")
        if weight_proof.recent_chain_data[-1].header_hash != peak.header_hash:
            raise Exception("weight proof peak hash does not match peak")

        old_proof = self.wallet_state_manager.blockchain.synced_weight_proof
        block_records = await self._weight_proof_handler.validate_weight_proof(weight_proof, False, old_proof)

        await self.wallet_state_manager.blockchain.new_valid_weight_proof(weight_proof, block_records)

```
