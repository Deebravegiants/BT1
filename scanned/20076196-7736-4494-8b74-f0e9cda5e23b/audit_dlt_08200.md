# [?] fix test: race condition w/ data budget (#10807)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-02-24
Source: https://github.com/anza-xyz/agave/commit/d42d9b2eda8c07365ee7cef8c18e849cb318a99b
Type: security-commit

## Details
fix test: race condition w/ data budget (#10807)

fix: test race data budget

## Patch
### core/src/repair/serve_repair.rs
```diff
@@ -906,7 +906,7 @@ impl ServeRepair {
             .spawn(move || {
                 let mut last_print = Instant::now();
                 let mut stats = ServeRepairStats::default();
-                let data_budget = DataBudget::default();
+                let data_budget = DataBudget::new(MAX_BYTES_PER_INTERVAL);
                 while !exit.load(Ordering::Relaxed) {
                     let result = self.run_listen(
                         &mut ping_cache,
```

### perf/src/data_budget.rs
```diff
@@ -10,6 +10,13 @@ pub struct DataBudget {
 }
 
 impl DataBudget {
+    pub fn new(bytes: usize) -> Self {
+        Self {
+            bytes: AtomicUsize::new(bytes),
+            asof: AtomicU64::new(solana_time_utils::timestamp()),
+        }
+    }
+
     /// Create a data budget with max bytes, used for tests
     pub fn restricted() -> Self {
         Self {
```
