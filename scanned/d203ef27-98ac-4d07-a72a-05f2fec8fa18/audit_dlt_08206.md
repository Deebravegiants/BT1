# [?] Fix: decayed_counter can overflow if shifted more than 63 (#35054)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2024-02-02
Source: https://github.com/solana-labs/solana/commit/bf95f65ce1501644719947ba07317fab94206a4f
Type: security-commit

## Details
Fix: decayed_counter can overflow if shifted more than 63 (#35054)

## Patch
### program-runtime/src/loaded_programs.rs
```diff
@@ -464,7 +464,8 @@ impl LoadedProgram {
 
     pub fn decayed_usage_counter(&self, now: Slot) -> u64 {
         let last_access = self.latest_access_slot.load(Ordering::Relaxed);
-        let decaying_for = now.saturating_sub(last_access);
+        // Shifting the u64 value for more than 63 will cause an overflow.
+        let decaying_for = std::cmp::min(63, now.saturating_sub(last_access));
         self.tx_usage_counter.load(Ordering::Relaxed) >> decaying_for
     }
 }
@@ -1359,6 +1360,10 @@ mod tests {
         assert_eq!(program.decayed_usage_counter(19), 16);
         assert_eq!(program.decayed_usage_counter(20), 8);
         assert_eq!(program.decayed_usage_counter(21), 4);
+
+        // Decay for 63 or more slots
+        assert_eq!(program.decayed_usage_counter(18 + 63), 0);
+        assert_eq!(program.decayed_usage_counter(100), 0);
     }
 
     #[test]
```
