# [?] [SEC-615] Reject malformed weight proof segments with overflow block at index 0 (#20747)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-04-02
Source: https://github.com/Chia-Network/chia-blockchain/commit/2fcaf4520c3b66c1db602f5df638ce9c9661ffe6
Type: security-commit

## Details
[SEC-615] Reject malformed weight proof segments with overflow block at index 0 (#20747)

* Reject malformed weight proof segments with overflow block at index 0

Add a bounds check in __validate_pospace before accessing
segment.sub_slots[idx - 1] on the overflow path. When idx == 0,
Python's negative indexing silently reads the last element instead of a
predecessor slot. This mirrors the existing guard in
_get_challenge_block_vdfs and returns None (same pattern as other
validation failures in this function).

* Add test for overflow block at sub-slot index 0 rejection

Exercises the new idx < 1 guard in __validate_pospace to achieve 100%
diff coverage on the defensive bounds check.

## Patch
### chia/_tests/weight_proof/test_weight_proof.py
```diff
@@ -1,16 +1,32 @@
 from __future__ import annotations
 
 import pytest
-from chia_rs import BlockRecord, ConsensusConstants, FullBlock, HeaderBlock, SubEpochSummary
+from chia_rs import (
+    BlockRecord,
+    ConsensusConstants,
+    FullBlock,
+    HeaderBlock,
+    SubEpochChallengeSegment,
+    SubEpochSummary,
+    SubSlotData,
+)
 from chia_rs.sized_bytes import bytes32
-from chia_rs.sized_ints import uint32
+from chia_rs.sized_ints import uint8, uint32, uint64
 
 from chia._tests.conftest import ConsensusMode
 from chia._tests.util.blockchain_mock import BlockchainMock
+from chia.consensus.default_constants import DEFAULT_CONSTANTS
 from chia.consensus.full_block_to_block_record import block_to_block_record
 from chia.consensus.generator_tools import get_block_header
 from chia.consensus.pot_iterations import validate_pospace_and_get_required_iters
-from chia.full_node.weight_proof import WeightProofHandler, _map_sub_epoch_summaries, _validate_summaries_weight
+from chia.full_node.weight_proof import (
+    WeightProofHandler,
+    _map_sub_epoch_summaries,
+    _validate_summaries_weight,
+)
+from chia.full_node.weight_proof import (
+    __validate_pospace as _validate_pospace_impl,
+)
 from chia.simulator.block_tools import BlockTools
 
 
@@ -516,3 +532,33 @@ async def test_weight_proof_extend_multiple_ses(
         valid, fork_point, _ = await wpf.validate_weight_proof(new_wp)
         assert valid
         assert fork_point != 0
+
+    def test_validate_pospace_rejects_overflow_at_idx_0(self) -> None:
+        constants = DEFAULT_CONSTANTS
+        overflow_spi = uint8(constants.NUM_SPS_SUB_SLOT - 1)
+        overflow_sub_slot = SubSlotData(
+            None,  # proof_of_space
+            None,  # cc_signage_point
+            None,  # cc_infusion_point
+            None,  # icc_infusion_point
+            None,  # cc_sp_vdf_info
+            overflow_spi,  # signage_point_index
+            None,  # cc_slot_end
+            None,  # icc_slot_end
+            None,  # cc_slot_end_info
+            None,  # icc_slot_end_info
+            None,  # cc_ip_vdf_info
+            None,  # icc_ip_vdf_info
+            None,  # total_iters
+        )
+        segment = SubEpochChallengeSegment(uint32(0), [overflow_sub_slot], None)
+        result = _validate_pospace_impl(
+            constants,
+            segment,
+            0,
+            uint64(constants.DIFFICULTY_STARTING),
+            None,
+            True,
+            uint32(0),
+        )
+        assert result is None
```

### chia/full_node/weight_proof.py
```diff
@@ -1371,6 +1371,9 @@ def __validate_pospace(
     sub_slot_data: SubSlotData = segment.sub_slots[idx]
 
     if sub_slot_data.signage_point_index and is_overflow_block(constants, sub_slot_data.signage_point_index):
+        if idx < 1:
+            log.error("overflow block at index 0 has no previous sub slot")
+            return None
         curr_slot = segment.sub_slots[idx - 1]
         assert curr_slot.cc_slot_end_info
         challenge = curr_slot.cc_slot_end_info.challenge
```
