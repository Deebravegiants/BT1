# [?] apollo_consensus_config: fix overflow in timeout calculation (#11932)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-01-25
Source: https://github.com/starkware-libs/sequencer/commit/4571d33b5577e16f5f7e31a634b5dd36143ff331
Type: security-commit

## Details
apollo_consensus_config: fix overflow in timeout calculation (#11932)

## Patch
### crates/apollo_consensus_config/src/config.rs
```diff
@@ -167,7 +167,7 @@ impl Timeout {
 
     /// Compute the timeout for the given round: min(base + round * delta, max).
     fn get_timeout(&self, round: u32) -> Duration {
-        (self.base + round * self.delta).min(self.max)
+        (self.base + self.delta.saturating_mul(round)).min(self.max)
     }
 }
 
```
