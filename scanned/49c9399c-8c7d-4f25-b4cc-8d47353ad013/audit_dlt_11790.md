# [?] Fix SSZ underflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/consensus-specs
Published: 2021-10-15
Source: https://github.com/ethereum/consensus-specs/commit/e70ef11b4d32473caf989ea3f61d09d596800767
Type: security-commit

## Details
Fix SSZ underflow

## Patch
### tests/core/pyspec/eth2spec/test/helpers/random.py
```diff
@@ -53,7 +53,7 @@ def exit_random_validators(spec, state, rng, fraction=0.5, exit_epoch=None, with
     """
     if from_epoch is None:
         from_epoch = spec.MAX_SEED_LOOKAHEAD + 1
-    epoch_diff = from_epoch - spec.get_current_epoch(state)
+    epoch_diff = int(from_epoch) - int(spec.get_current_epoch(state))
     for _ in range(epoch_diff):
         # NOTE: if `epoch_diff` is negative, then this loop body does not execute.
         next_epoch(spec, state)
```
