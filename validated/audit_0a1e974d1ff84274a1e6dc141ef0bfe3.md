### Title
Unbounded Iteration Over Attacker-Controlled `sub_epochs` in Weight Proof Validation Blocks the Event Loop — (`File: chia/full_node/weight_proof.py`)

### Summary
`_validate_sub_epoch_summaries` iterates synchronously over the entire `weight_proof.sub_epochs` list — which is fully attacker-controlled — without any size check before processing. An unprivileged peer can send a crafted `RespondProofOfWeight` message containing millions of `SubEpochData` entries, causing the asyncio event loop to be blocked for an extended period and preventing the node or wallet from processing any valid blocks or sync messages during that time.

### Finding Description

When a full node or wallet needs to sync, it requests a weight proof from a peer via `RequestProofOfWeight`. The peer responds with a `RespondProofOfWeight` containing a `WeightProof` object. The `WeightProof` type is:

```python
class WeightProof(Streamable):
    sub_epochs: list[SubEpochData]          # unbounded, attacker-controlled
    sub_epoch_segments: list[SubEpochChallengeSegment]
    recent_chain_data: list[HeaderBlock]
``` [1](#0-0) 

The validation entry point for both full nodes and wallets calls `_validate_sub_epoch_summaries` **synchronously** in the asyncio event loop, before any worker process is involved:

```python
async def validate_weight_proof(self, weight_proof: WeightProof) -> ...:
    summaries, sub_epoch_weight_list = _validate_sub_epoch_summaries(self.constants, weight_proof)
    await asyncio.sleep(0)  # break up otherwise multi-second sync code
    ...
    with ProcessPoolExecutor(...) as executor:   # heavy work goes here, AFTER the blocking call
        ...
``` [2](#0-1) 

`_validate_sub_epoch_summaries` immediately calls `_map_sub_epoch_summaries`, which iterates over every entry in `weight_proof.sub_epochs` with no size guard:

```python
def _validate_sub_epoch_summaries(constants, weight_proof):
    ...
    summaries, total, sub_epoch_weight_list = _map_sub_epoch_summaries(
        constants.SUB_EPOCH_BLOCKS,
        constants.GENESIS_CHALLENGE,
        weight_proof.sub_epochs,      # ← no length check before this call
        constants.DIFFICULTY_STARTING,
    )
``` [3](#0-2) 

Inside `_map_sub_epoch_summaries`, every element is processed unconditionally:

```python
def _map_sub_epoch_summaries(sub_blocks_for_se, ses_hash, sub_epoch_data, curr_difficulty):
    summaries: list[SubEpochSummary] = []
    sub_epoch_weight_list: list[uint128] = []
    for idx, data in enumerate(sub_epoch_data):   # ← O(N) with no bound
        ses = SubEpochSummary(ses_hash, data.reward_chain_hash, ...)
        ...
        summaries.append(ses)
    ...
    return summaries, total_weight, sub_epoch_weight_list
``` [4](#0-3) 

The same unbounded pattern applies in the wallet's `WalletWeightProofHandler.validate_weight_proof`: [5](#0-4) 

The only pre-validation checks performed on the received `WeightProof` before this call are on `recent_chain_data[-1].height` and `.weight` — there is no check on `len(weight_proof.sub_epochs)`: [6](#0-5) 

### Impact Explanation

Because `_map_sub_epoch_summaries` runs synchronously in the asyncio event loop (not in a worker process), a crafted weight proof with N million `SubEpochData` entries will block the event loop for O(N) time and consume O(N) memory. During this period:

- The full node cannot process incoming blocks, peer messages, or mempool transactions.
- The wallet node cannot process coin state updates or new peaks.

If the attacker controls even a small number of IP addresses, they can chain these attacks — each crafted weight proof from a new peer IP blocks the node for the duration of processing before the peer is banned. This constitutes a **long-lived inability** for honest nodes and wallets to process valid blocks and sync updates.

### Likelihood Explanation

Any unprivileged peer can connect to a full node, advertise a higher peak (with a valid height/weight in `recent_chain_data[-1]`), and respond to the resulting `RequestProofOfWeight` with a crafted `RespondProofOfWeight` containing an arbitrarily large `sub_epochs` list. No keys, admin access, or cryptographic breaks are required. The attack is reachable from the standard peer-to-peer connection path.

### Recommendation

Add an explicit size check on `weight_proof.sub_epochs` before calling `_map_sub_epoch_summaries`. The maximum legitimate number of sub-epochs is bounded by `peak_height / SUB_EPOCH_BLOCKS`. Reject any weight proof whose `sub_epochs` list exceeds this bound (with a reasonable safety margin). For example:

```python
max_sub_epochs = (peak_height // constants.SUB_EPOCH_BLOCKS) + 2
if len(weight_proof.sub_epochs) > max_sub_epochs:
    log.error("weight proof has too many sub epochs")
    return None, None
```

This check should be placed at the top of `_validate_sub_epoch_summaries`, before any iteration begins.

### Proof of Concept

1. Attacker node connects to victim full node as a peer.
2. Attacker sends `NewPeak` advertising a height/weight higher than the victim's current peak, with a valid `recent_chain_data[-1]` matching those values.
3. Victim calls `request_validate_wp`, which sends `RequestProofOfWeight` to the attacker.
4. Attacker responds with `RespondProofOfWeight` containing a `WeightProof` where `sub_epochs` is a list of 10,000,000 `SubEpochData` entries (each minimal in size).
5. Victim's `validate_weight_proof` calls `_validate_sub_epoch_summaries` → `_map_sub_epoch_summaries`, which iterates over all 10 million entries synchronously in the event loop.
6. The event loop is blocked for an extended period; the node cannot process any valid blocks, peer messages, or wallet updates during this time.
7. Eventually `_validate_summaries_weight` returns `False` (the fabricated summaries don't match `recent_chain_data`), the attacker peer is banned, but the damage (event loop stall) has already occurred.
8. Repeating from a new IP restarts the attack. [4](#0-3) [7](#0-6) [2](#0-1)

### Citations

**File:** chia/types/weight_proof.py (L40-45)
```python
@streamable
@dataclass(frozen=True)
class WeightProof(Streamable):
    sub_epochs: list[SubEpochData]
    sub_epoch_segments: list[SubEpochChallengeSegment]  # sampled sub epoch
    recent_chain_data: list[HeaderBlock]
```

**File:** chia/full_node/weight_proof.py (L605-616)
```python
    async def validate_weight_proof(self, weight_proof: WeightProof) -> tuple[bool, uint32, list[SubEpochSummary]]:
        assert self.blockchain is not None
        if len(weight_proof.sub_epochs) == 0:
            return False, uint32(0), []

        # timing reference: start
        summaries, sub_epoch_weight_list = _validate_sub_epoch_summaries(self.constants, weight_proof)
        await asyncio.sleep(0)  # break up otherwise multi-second sync code
        # timing reference: 1 second
        if summaries is None or sub_epoch_weight_list is None:
            log.error("weight proof failed sub epoch data validation")
            return False, uint32(0), []
```

**File:** chia/full_node/weight_proof.py (L848-878)
```python
def _validate_sub_epoch_summaries(
    constants: ConsensusConstants,
    weight_proof: WeightProof,
) -> tuple[list[SubEpochSummary] | None, list[uint128] | None]:
    last_ses_hash, last_ses_sub_height = _get_last_ses_hash(constants, weight_proof.recent_chain_data)
    if last_ses_hash is None:
        log.warning("could not find last ses block")
        return None, None

    summaries, total, sub_epoch_weight_list = _map_sub_epoch_summaries(
        constants.SUB_EPOCH_BLOCKS,
        constants.GENESIS_CHALLENGE,
        weight_proof.sub_epochs,
        constants.DIFFICULTY_STARTING,
    )

    log.info(f"validating {len(summaries)} sub epochs")

    # validate weight
    if not _validate_summaries_weight(constants, total, summaries, weight_proof):
        log.error("failed validating weight")
        return None, None

    last_ses = summaries[-1]
    log.debug(f"last ses sub height {last_ses_sub_height}")
    # validate last ses_hash
    if last_ses.get_hash() != last_ses_hash:
        log.error(f"failed to validate ses hashes block height {last_ses_sub_height}")
        return None, None

    return summaries, sub_epoch_weight_list
```

**File:** chia/full_node/weight_proof.py (L881-920)
```python
def _map_sub_epoch_summaries(
    sub_blocks_for_se: uint32,
    ses_hash: bytes32,
    sub_epoch_data: list[SubEpochData],
    curr_difficulty: uint64,
) -> tuple[list[SubEpochSummary], uint128, list[uint128]]:
    total_weight: uint128 = uint128(0)
    summaries: list[SubEpochSummary] = []
    sub_epoch_weight_list: list[uint128] = []
    for idx, data in enumerate(sub_epoch_data):
        ses = SubEpochSummary(
            ses_hash,
            data.reward_chain_hash,
            data.num_blocks_overflow,
            data.new_difficulty,
            data.new_sub_slot_iters,
            data.challenge_merkle_root,
        )

        if idx < len(sub_epoch_data) - 1:
            delta = 0
            if idx > 0:
                delta = data.num_blocks_overflow
            log.debug(f"sub epoch {idx} start weight is {total_weight + curr_difficulty} ")
            sub_epoch_weight_list.append(uint128(total_weight + curr_difficulty))
            total_weight = uint128(
                total_weight
                + curr_difficulty * (sub_blocks_for_se + sub_epoch_data[idx + 1].num_blocks_overflow - delta)
            )

        # if new epoch update diff and iters
        if data.new_difficulty is not None:
            curr_difficulty = data.new_difficulty

        # add to dict
        summaries.append(ses)
        ses_hash = std_hash(ses)
    # add last sub epoch weight
    sub_epoch_weight_list.append(uint128(total_weight + curr_difficulty))
    return summaries, total_weight, sub_epoch_weight_list
```

**File:** chia/wallet/wallet_weight_proof_handler.py (L45-67)
```python
    async def validate_weight_proof(
        self, weight_proof: WeightProof, skip_segment_validation: bool = False, old_proof: WeightProof | None = None
    ) -> list[BlockRecord]:
        start_time = time.time()
        summaries, sub_epoch_weight_list = _validate_sub_epoch_summaries(self._constants, weight_proof)
        await asyncio.sleep(0)  # break up otherwise multi-second sync code
        if summaries is None or sub_epoch_weight_list is None:
            raise ValueError("weight proof failed sub epoch data validation")
        validate_from = get_fork_ses_idx(old_proof, weight_proof)
        valid, block_records = await validate_weight_proof_inner(
            self._constants,
            self._executor,
            self._executor_shutdown_tempfile.name,
            self._num_processes,
            weight_proof,
            summaries,
            sub_epoch_weight_list,
            skip_segment_validation,
            validate_from,
        )
        if not valid:
            raise ValueError("weight proof validation failed")
        log.info(f"It took {time.time() - start_time} time to validate the weight proof {weight_proof.get_hash()}")
```

**File:** chia/full_node/full_node.py (L1167-1184)
```python
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
```
