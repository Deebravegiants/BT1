# [?] Change mainnet `TERMINAL_TOTAL_DIFFICULTY` placeholder to `2**256-2**10` to avoid overflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/consensus-specs
Published: 2021-09-27
Source: https://github.com/ethereum/consensus-specs/commit/ef51e1cfb9a9ad3f22357ffd0ac95b03c6449581
Type: security-commit

## Details
Change mainnet `TERMINAL_TOTAL_DIFFICULTY` placeholder to `2**256-2**10` to avoid overflow

## Patch
### configs/mainnet.yaml
```diff
@@ -5,8 +5,8 @@ PRESET_BASE: 'mainnet'
 
 # Transition
 # ---------------------------------------------------------------
-# TBD, 2**256-1 is a placeholder
-TERMINAL_TOTAL_DIFFICULTY: 115792089237316195423570985008687907853269984665640564039457584007913129639935
+# TBD, 2**256-2**10 is a placeholder
+TERMINAL_TOTAL_DIFFICULTY: 115792089237316195423570985008687907853269984665640564039457584007913129638912
 
 
 # Genesis
```

### tests/core/pyspec/eth2spec/test/merge/fork_choice/test_on_merge_block.py
```diff
@@ -1,6 +1,6 @@
 from eth2spec.utils.ssz.ssz_typing import uint256
 from eth2spec.test.exceptions import BlockNotFoundException
-from eth2spec.test.context import spec_state_test, with_phases, with_presets, MERGE, MINIMAL
+from eth2spec.test.context import spec_state_test, with_phases, MERGE
 from eth2spec.test.helpers.block import (
     build_empty_block_for_next_slot,
 )
@@ -46,7 +46,6 @@ def wrap(flag: AtomicBoolean):
 
 
 @with_phases([MERGE])
-@with_presets([MINIMAL], reason="mainnet `TERMINAL_TOTAL_DIFFICULTY` stub would cause overflow")
 @spec_state_test
 def test_all_valid(spec, state):
     test_steps = []
@@ -81,7 +80,6 @@ def run_func():
 
 
 @with_phases([MERGE])
-@with_presets([MINIMAL], reason="mainnet `TERMINAL_TOTAL_DIFFICULTY` stub would cause overflow")
 @spec_state_test
 def test_block_lookup_failed(spec, state):
     test_steps = []
@@ -112,7 +110,6 @@ def run_func():
 
 
 @with_phases([MERGE])
-@with_presets([MINIMAL], reason="mainnet `TERMINAL_TOTAL_DIFFICULTY` stub would cause overflow")
 @spec_state_test
 def test_too_early_for_merge(spec, state):
     test_steps = []
@@ -145,7 +142,6 @@ def run_func():
 
 
 @with_phases([MERGE])
-@with_presets([MINIMAL], reason="mainnet `TERMINAL_TOTAL_DIFFICULTY` stub would cause overflow")
 @spec_state_test
 def test_too_late_for_merge(spec, state):
     test_steps = []
```
