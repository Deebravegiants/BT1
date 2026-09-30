# [?] [CHIA-4231] Fix stale overflow (#20924)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-06-04
Source: https://github.com/Chia-Network/chia-blockchain/commit/b2b9830c11939b21136745586465091c8874bfac
Type: security-commit

## Details
[CHIA-4231] Fix stale overflow (#20924)

* regression test and fix

* lint

* simplify code

* cleaner

* refactor

## Patch
### chia/_tests/timelord/test_new_peak.py
```diff
@@ -18,7 +18,7 @@
 from chia.simulator.block_tools import BlockTools
 from chia.simulator.full_node_simulator import FullNodeSimulator
 from chia.simulator.wallet_tools import WalletTool
-from chia.timelord.timelord_api import TimelordAPI
+from chia.timelord.timelord_api import TimelordAPI, overflow_sp_total_iters
 
 
 def last_unfinished(tl: TimelordAPI, *, overflow: bool) -> timelord_protocol.NewUnfinishedBlockTimelord:
@@ -28,6 +28,39 @@ def last_unfinished(tl: TimelordAPI, *, overflow: bool) -> timelord_protocol.New
         return tl.timelord.unfinished_blocks[-1]
 
 
+@pytest.mark.parametrize(
+    "overflow_ip_total_iters, ip_iters, sp_iters, sub_slot_iters, expected_sp_total_iters",
+    [
+        (1050, uint64(50), uint64(900), uint64(1000), 900),
+        (5050, uint64(50), uint64(900), uint64(1000), 4900),
+        (9999, uint64(999), uint64(960), uint64(1000), 8960),
+        (2**80 + 90, uint64(90), uint64(2**20 - 1), uint64(2**20), 2**80 - 1),
+    ],
+)
+def test_overflow_sp_total_iters(
+    overflow_ip_total_iters: int,
+    ip_iters: uint64,
+    sp_iters: uint64,
+    sub_slot_iters: uint64,
+    expected_sp_total_iters: int,
+) -> None:
+    assert (
+        overflow_sp_total_iters(overflow_ip_total_iters, ip_iters, sp_iters, sub_slot_iters) == expected_sp_total_iters
+    )
+
+
+def test_overflow_sp_total_iters_uses_previous_slot() -> None:
+    overflow_ip_total_iters = 5050
+    ip_iters = uint64(50)
+    sp_iters = uint64(900)
+    sub_slot_iters = uint64(1000)
+
+    ip_slot_start_total_iters = overflow_ip_total_iters - int(ip_iters)
+
+    assert ip_slot_start_total_iters == 5000
+    assert overflow_sp_total_iters(overflow_ip_total_iters, ip_iters, sp_iters, sub_slot_iters) == 4900
+
+
 class TestNewPeak:
     @pytest.mark.anyio
     async def test_timelord_new_peak_basic(
@@ -342,6 +375,92 @@ async def test_timelord_new_peak_unfinished_orphaned_overflow(
                     == peak.reward_chain_block.get_hash()
                 )
 
+    @pytest.mark.anyio
+    # todo_v2_plots remove limit_consensus_modes when this test uses a real unfinished block for HF3.0.
+    @pytest.mark.limit_consensus_modes(
+        allowed=[
+            ConsensusMode.PLAIN,
+            ConsensusMode.HARD_FORK_2_0,
+            ConsensusMode.SOFT_FORK_2_7,
+        ],
+        reason="test builds a synthetic unfinished block for HF3.0",
+    )
+    async def test_timelord_new_peak_stale_overflow_does_not_block_peak(
+        self, bt: BlockTools, timelord: tuple[TimelordAPI, ChiaServer], default_1000_blocks: list[FullBlock]
+    ) -> None:
+        async with create_blockchain(bt.constants, 2) as (b1, _):
+            async with create_blockchain(bt.constants, 2) as (b2, _):
+                timelord_api, _ = timelord
+                for block in default_1000_blocks:
+                    await _validate_and_add_block(b1, block)
+                    await _validate_and_add_block(b2, block)
+
+                peak = timelord_peak_from_block(b1, default_1000_blocks[-1])
+                assert peak is not None
+                await timelord_api.new_peak_timelord(peak)
+                await time_out_assert(60, tl_new_peak_is_none, True, timelord_api)
+                assert timelord_api.timelord.last_state.peak is not None
+
+                overflow_block = bt.get_consecutive_blocks(
+                    1, default_1000_blocks, time_per_block=9, force_overflow=True
+                )[-1]
+                later_peak_block = bt.get_consecutive_blocks(
+                    1,
+                    default_1000_blocks,
+                    seed=b"data",
+                    time_per_block=50,
+                    skip_slots=1,
+                    min_signage_point=overflow_block.reward_chain_block.signage_point_index,
+                )[-1]
+                assert later_peak_block.total_iters >= overflow_block.total_iters
+                assert len(later_peak_block.finished_sub_slots) > 0
+
+                await _validate_and_add_block(b1, overflow_block)
+                await _validate_and_add_block(b2, later_peak_block)
+
+                block_record = b1.block_record(overflow_block.header_hash)
+                sub_slot_iters, difficulty = get_next_sub_slot_iters_and_difficulty(
+                    bt.constants,
+                    len(overflow_block.finished_sub_slots) > 0,
+                    b1.block_record(overflow_block.prev_header_hash),
+                    b1,
+                )
+                stale_overflow = timelord_protocol.NewUnfinishedBlockTimelord(
+                    overflow_block.reward_chain_block.get_unfinished(),
+                    difficulty,
+                    sub_slot_iters,
+                    overflow_block.foliage,
+                    next_sub_epoch_summary(bt.constants, b1, block_record.required_iters, overflow_block, True),
+                    await get_rc_prev(b1, overflow_block),
+                    None,
+                )
+                await timelord_api.new_unfinished_block_timelord(stale_overflow)
+                assert timelord_api.timelord.overflow_blocks[-1].get_hash() == stale_overflow.get_hash()
+
+                later_peak = timelord_peak_from_block(b2, later_peak_block)
+                timelord_api.timelord.last_state.set_state(later_peak)
+                assert timelord_api.timelord._can_infuse_unfinished_block(stale_overflow) is None
+                await timelord_api.timelord._reset_chains()
+
+                next_peak_block = bt.get_consecutive_blocks(
+                    1,
+                    [*default_1000_blocks, later_peak_block],
+                    seed=b"next",
+                    skip_overflow=True,
+                )[-1]
+                await _validate_and_add_block(b2, next_peak_block)
+
+                next_peak = timelord_peak_from_block(b2, next_peak_block)
+                assert stale_overflow.reward_chain_block.total_iters <= next_peak.reward_chain_block.total_iters
+                await timelord_api.new_peak_timelord(next_peak)
+                await time_out_assert(60, tl_new_peak_is_none, True, timelord_api)
+
+                assert (
+                    timelord_api.timelord.last_state.peak is not None
+                    and timelord_api.timelord.last_state.peak.reward_chain_block.get_hash()
+                    == next_peak.reward_chain_block.get_hash()
+                )
+
     @pytest.mark.anyio
     async def test_timelord_new_peak_unfinished_eos(
         self,
```

### chia/timelord/timelord.py
```diff
@@ -368,10 +368,16 @@ async def _reset_chains(self, *, first_run: bool = False, only_eos: bool = False
         # Remove all unfinished blocks that have already passed.
         self.unfinished_blocks = new_unfinished_blocks
 
-        # remove overflow blocks that were moved to unfinished cache
-        for block in new_unfinished_blocks:
-            if block in self.overflow_blocks:
-                self.overflow_blocks.remove(block)
+        new_overflow_blocks = []
+        for block in self.overflow_blocks:
+            # Skip overflow blocks that were moved to the unfinished cache.
+            if block in new_unfinished_blocks:
+                continue
+            # Skip stale overflow blocks that have already passed.
+            if block.reward_chain_block.total_iters <= self.last_state.get_total_iters():
+                continue
+            new_overflow_blocks.append(block)
+        self.overflow_blocks = new_overflow_blocks
         # Signage points.
         if not only_eos and len(self.signage_point_iters) > 0:
             count_signage = 0
```

### chia/timelord/timelord_api.py
```diff
@@ -12,11 +12,17 @@
 from chia.server.api_protocol import ApiMetadata
 from chia.timelord.iters_from_block import iters_from_block
 from chia.timelord.timelord import Timelord
-from chia.timelord.types import Chain, IterationType
+from chia.timelord.types import Chain, IterationType, StateType
 
 log = logging.getLogger(__name__)
 
 
+def overflow_sp_total_iters(
+    overflow_ip_total_iters: int, ip_iters: uint64, sp_iters: uint64, sub_slot_iters: uint64
+) -> int:
+    return overflow_ip_total_iters - int(ip_iters) + int(sp_iters) - int(sub_slot_iters)
+
+
 class TimelordAPI:
     if TYPE_CHECKING:
         from chia.apis.timelord_stub import TimelordApiStub
@@ -39,6 +45,17 @@ def ready(self) -> bool:
     def _set_state_changed_callback(self, callback: StateChangedProtocol) -> None:
         self.timelord.state_changed_callback = callback
 
+    def _schedule_unfinished_block(
+        self, new_unfinished_block: timelord_protocol.NewUnfinishedBlockTimelord, new_block_iters: uint64
+    ) -> None:
+        self.timelord.unfinished_blocks.append(new_unfinished_block)
+        for chain in [Chain.REWARD_CHAIN, Chain.CHALLENGE_CHAIN]:
+            self.timelord.iters_to_submit[chain].append(new_block_iters)
+        if self.timelord.last_state.get_deficit() < self.timelord.constants.MIN_BLOCKS_PER_CHALLENGE_BLOCK:
+            self.timelord.iters_to_submit[Chain.INFUSED_CHALLENGE_CHAIN].append(new_block_iters)
+        self.timelord.iteration_to_proof_type[new_block_iters] = IterationType.INFUSION_POINT
+        self.timelord.total_unfinished += 1
+
     @metadata.request()
     async def new_peak_timelord(self, new_peak: NewPeakTimelord) -> None:
         if self.timelord.last_state is None:
@@ -144,18 +161,42 @@ async def new_unfinished_block_timelord(
                 return None
             last_ip_iters = self.timelord.last_state.get_last_ip()
             if sp_iters > ip_iters:
+                current_total_iters = int(self.timelord.last_state.get_total_iters())
+                overflow_ip_total_iters = int(new_unfinished_block.reward_chain_block.total_iters)
+                # If the IP is already behind us, this overflow block can only block future peaks.
+                if overflow_ip_total_iters <= current_total_iters:
+                    log.debug(f"Dropping stale overflow unfinished block, total {self.timelord.total_unfinished}")
+                    return None
+                # Before EOS, keep overflow blocks cached until the slot boundary arrives.
+                if self.timelord.last_state.state_type != StateType.END_OF_SUB_SLOT:
+                    self.timelord.overflow_blocks.append(new_unfinished_block)
+                    log.debug(f"Overflow unfinished block, total {self.timelord.total_unfinished}")
+                    return None
+                # Schedule late overflow only when this EOS is between its SP and IP.
+                if (
+                    overflow_sp_total_iters(
+                        overflow_ip_total_iters, ip_iters, sp_iters, self.timelord.last_state.get_sub_slot_iters()
+                    )
+                    >= current_total_iters
+                ):
+                    self.timelord.overflow_blocks.append(new_unfinished_block)
+                    log.debug(f"Overflow unfinished block, total {self.timelord.total_unfinished}")
+                    return None
+                overflow_iters = self.timelord._can_infuse_unfinished_block(new_unfinished_block)
+                # The overflow is in this EOS window and can be infused now.
+                if overflow_iters:
+                    self._schedule_unfinished_block(new_unfinished_block, overflow_iters)
+                    log.debug(f"Late overflow unfinished block, total {self.timelord.total_unfinished}")
+                    return None
+                # Keep still-future overflow blocks if local state cannot infuse them yet.
                 self.timelord.overflow_blocks.append(new_unfinished_block)
                 log.debug(f"Overflow unfinished block, total {self.timelord.total_unfinished}")
+                return None
             elif ip_iters > last_ip_iters:
                 new_block_iters: uint64 | None = self.timelord._can_infuse_unfinished_block(new_unfinished_block)
+                # Non-overflow blocks can be scheduled immediately when the IP is still ahead.
                 if new_block_iters:
-                    self.timelord.unfinished_blocks.append(new_unfinished_block)
-                    for chain in [Chain.REWARD_CHAIN, Chain.CHALLENGE_CHAIN]:
-                        self.timelord.iters_to_submit[chain].append(new_block_iters)
-                    if self.timelord.last_state.get_deficit() < self.timelord.constants.MIN_BLOCKS_PER_CHALLENGE_BLOCK:
-                        self.timelord.iters_to_submit[Chain.INFUSED_CHALLENGE_CHAIN].append(new_block_iters)
-                    self.timelord.iteration_to_proof_type[new_block_iters] = IterationType.INFUSION_POINT
-                    self.timelord.total_unfinished += 1
+                    self._schedule_unfinished_block(new_unfinished_block, new_block_iters)
                     log.debug(f"Non-overflow unfinished block, total {self.timelord.total_unfinished}")
 
     @metadata.request()
```
