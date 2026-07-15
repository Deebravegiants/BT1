### Title
Unbounded Weight Proof Generation Queue Enables Sync DoS via Costless `request_proof_of_weight` Flooding — (File: `chia/full_node/full_node_api.py`)

---

### Summary

Any unprivileged peer can send `request_proof_of_weight` messages for distinct valid block tips, each triggering expensive server-side weight proof computation. Because the `WeightProofHandler` serializes all proof generation behind a single `asyncio.Lock`, and because the per-peer rate limit (5/min) is not a global limit, an attacker controlling multiple IPs can queue an unbounded backlog of computations at zero on-chain cost, causing legitimate sync requests to time out and preventing honest nodes from syncing.

---

### Finding Description

`FullNodeAPI.request_proof_of_weight` in `chia/full_node/full_node_api.py` accepts any peer-supplied `tip` that resolves to a known block record and immediately invokes `WeightProofHandler.get_proof_of_weight`:

```python
# chia/full_node/full_node_api.py lines 359-397
@metadata.request(reply_types=[ProtocolMessageTypes.respond_proof_of_weight])
async def request_proof_of_weight(self, request: full_node_protocol.RequestProofOfWeight) -> Message | None:
    if self.full_node.blockchain.try_block_record(request.tip) is None:
        return None
    if request.tip in self.full_node.pow_creation:
        event = self.full_node.pow_creation[request.tip]
        await event.wait()
        wp = await self.full_node.weight_proof_handler.get_proof_of_weight(request.tip)
    else:
        event = asyncio.Event()
        self.full_node.pow_creation[request.tip] = event
        wp = await self.full_node.weight_proof_handler.get_proof_of_weight(request.tip)
        event.set()
``` [1](#0-0) 

`get_proof_of_weight` acquires a **global `asyncio.Lock`** before calling `_create_proof_of_weight`, which performs extensive database reads (all sub-epoch block records, segment data), computes sub-epoch challenge segments, and serializes a weight proof that can reach 50 MB:

```python
# chia/full_node/weight_proof.py lines 82-101
async def get_proof_of_weight(self, tip: bytes32) -> WeightProof | None:
    ...
    async with self.lock:
        if self.proof is not None:
            if self.proof.recent_chain_data[-1].header_hash == tip:
                return self.proof
        wp = await self._create_proof_of_weight(tip)
        ...
``` [2](#0-1) 

The `pow_creation` dict deduplicates requests **only for the same tip hash**. Requests for distinct valid tips each trigger a separate, serialized, expensive computation. The chain contains thousands of valid tips (any block above `WEIGHT_PROOF_RECENT_BLOCKS` height passes the guard at line 88).

The rate limit for `request_proof_of_weight` is **5 messages per 60 seconds per peer connection**:

```python
ProtocolMessageTypes.request_proof_of_weight: RLSettings(True, 5, 100),
``` [3](#0-2) 

Under v3 rate limits, the per-peer in-flight window is 2:

```python
ProtocolMessageTypes.request_proof_of_weight: RLSettingsV3(window_size=2),
``` [4](#0-3) 

These limits are **per-connection**, not global. An attacker controlling N IPs can each send 5 requests/min for distinct tips, queuing N×5 expensive computations per minute behind the single `asyncio.Lock`. There is no global concurrency cap, no per-node request budget, and no on-chain cost to the attacker.

---

### Impact Explanation

The `WeightProofHandler.lock` serializes all proof generation. Each `_create_proof_of_weight` call reads all sub-epoch block records, computes challenge segments, and serializes up to 50 MB of data — a multi-second operation on a long chain. With an attacker queuing hundreds of requests per minute for distinct tips, the lock is held continuously. Legitimate nodes initiating sync call `request_validate_wp` with a 360-second timeout:

```python
wp_timeout = 360
...
response = await weight_proof_peer.call_api(FullNodeAPI.request_proof_of_weight, request, timeout=wp_timeout)
if response is None or not isinstance(response, full_node_protocol.RespondProofOfWeight):
    await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
    raise RuntimeError(...)
``` [5](#0-4) 

If the queue backlog exceeds 360 seconds of computation, the legitimate sync peer times out, the target node is banned, and sync fails. This constitutes a **long-lived inability for honest nodes to process sync updates** under normal network assumptions.

---

### Likelihood Explanation

- Requires only multiple IP addresses (no keys, no funds, no privileged access).
- Valid tips are abundant on a live chain (any block above `WEIGHT_PROOF_RECENT_BLOCKS`).
- The per-peer rate limit (5/min) is the only guard; it is not global.
- The attack is cheap: no on-chain transactions, no fees, no stake.
- Nodes under active sync are the most vulnerable targets.

---

### Recommendation

1. **Add a global in-flight limit** on concurrent weight proof generation requests (e.g., reject or queue-drop if more than 1–2 computations are already pending globally, regardless of requester).
2. **Prioritize requests from peers that are actively syncing** (i.e., peers that sent `new_peak` with higher weight) over arbitrary inbound requests.
3. **Reduce the per-peer rate limit** for `request_proof_of_weight` further, or add a global aggregate cap across all peers.
4. **Return a cached proof for the current peak immediately** without acquiring the lock when the tip matches the cached tip, eliminating lock contention for the common case.

---

### Proof of Concept

1. Attacker connects to target node from N IPs (within the node's max-connection limit).
2. Each connection enumerates valid block hashes from the target's chain (via `request_block` or public explorers).
3. Each connection sends 5 `request_proof_of_weight` messages per minute, each for a distinct valid tip hash.
4. The `WeightProofHandler.lock` is held continuously as each unique tip triggers `_create_proof_of_weight`.
5. A legitimate node initiating sync sends `request_proof_of_weight` for the current peak; the response is delayed beyond the 360-second timeout.
6. The legitimate node calls `await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)` and fails to sync.

### Citations

**File:** chia/full_node/full_node_api.py (L359-397)
```python
    @metadata.request(reply_types=[ProtocolMessageTypes.respond_proof_of_weight])
    async def request_proof_of_weight(self, request: full_node_protocol.RequestProofOfWeight) -> Message | None:
        if self.full_node.weight_proof_handler is None:
            return None
        if self.full_node.blockchain.try_block_record(request.tip) is None:
            self.log.error(f"got weight proof request for unknown peak {request.tip}")
            return None
        if request.tip in self.full_node.pow_creation:
            event = self.full_node.pow_creation[request.tip]
            await event.wait()
            wp = await self.full_node.weight_proof_handler.get_proof_of_weight(request.tip)
        else:
            event = asyncio.Event()
            self.full_node.pow_creation[request.tip] = event
            wp = await self.full_node.weight_proof_handler.get_proof_of_weight(request.tip)
            event.set()
        tips = list(self.full_node.pow_creation.keys())

        if len(tips) > 4:
            # Remove old from cache
            for i in range(4):
                self.full_node.pow_creation.pop(tips[i])

        if wp is None:
            self.log.error(f"failed creating weight proof for peak {request.tip}")
            return None

        # Serialization of wp is slow
        if (
            self.full_node.full_node_store.serialized_wp_message_tip is not None
            and self.full_node.full_node_store.serialized_wp_message_tip == request.tip
        ):
            return self.full_node.full_node_store.serialized_wp_message
        message = make_msg(
            ProtocolMessageTypes.respond_proof_of_weight, full_node_protocol.RespondProofOfWeight(wp, request.tip)
        )
        self.full_node.full_node_store.serialized_wp_message_tip = request.tip
        self.full_node.full_node_store.serialized_wp_message = message
        return message
```

**File:** chia/full_node/weight_proof.py (L82-101)
```python
    async def get_proof_of_weight(self, tip: bytes32) -> WeightProof | None:
        tip_rec = self.blockchain.try_block_record(tip)
        if tip_rec is None:
            log.error("unknown tip")
            return None

        if tip_rec.height < self.constants.WEIGHT_PROOF_RECENT_BLOCKS:
            log.info(f"chain to short for weight proof. tip: {tip_rec.height}")
            return None

        async with self.lock:
            if self.proof is not None:
                if self.proof.recent_chain_data[-1].header_hash == tip:
                    return self.proof
            wp = await self._create_proof_of_weight(tip)
            if wp is None:
                return None
            self.proof = wp
            self.tip = tip
            return wp
```

**File:** chia/server/rate_limit_numbers.py (L95-95)
```python
        ProtocolMessageTypes.request_proof_of_weight: RLSettings(True, 5, 100),
```

**File:** chia/server/rate_limits_v3.py (L66-66)
```python
    ProtocolMessageTypes.request_proof_of_weight: RLSettingsV3(window_size=2),
```

**File:** chia/full_node/full_node.py (L1157-1166)
```python
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
```
