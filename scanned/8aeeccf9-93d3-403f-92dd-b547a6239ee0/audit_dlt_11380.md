# [?] fix(monty-31): eliminate twiddle cache race condition by merging into single lock (#1561)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-04-25
Source: https://github.com/Plonky3/Plonky3/commit/7a6895887780ef4e5ee0eecd73078a2b06f8f3ad
Type: security-commit

## Details
fix(monty-31): eliminate twiddle cache race condition by merging into single lock (#1561)

## Patch
### monty-31/src/dft/mod.rs
```diff
@@ -40,24 +40,38 @@ fn coset_shift_and_scale_rows<F: Field>(
         });
 }
 
+/// Paired twiddle and inverse-twiddle tables, always updated atomically
+/// under a single lock to prevent concurrent observers from seeing a
+/// half-updated state.
+#[derive(Clone, Debug)]
+struct TwiddlePair<F> {
+    twiddles: Arc<[Vec<F>]>,
+    inv_twiddles: Arc<[Vec<F>]>,
+}
+
+impl<F> Default for TwiddlePair<F> {
+    fn default() -> Self {
+        Self {
+            twiddles: Arc::from(Vec::new()),
+            inv_twiddles: Arc::from(Vec::new()),
+        }
+    }
+}
+
 /// Recursive DFT, decimation-in-frequency in the forward direction,
 /// decimation-in-time in the backward (inverse) direction.
 #[derive(Clone, Debug, Default)]
 pub struct RecursiveDft<F> {
-    /// Forward twiddle tables
-    #[allow(clippy::type_complexity)]
-    twiddles: Arc<RwLock<Arc<[Vec<F>]>>>,
-    /// Inverse twiddle tables
-    #[allow(clippy::type_complexity)]
-    inv_twiddles: Arc<RwLock<Arc<[Vec<F>]>>>,
+    /// Memoized twiddle factors, paired with their inverses.
+    ///
+    /// Both tables are stored behind a single lock so they are always
+    /// updated atomically.
+    cache: Arc<RwLock<TwiddlePair<F>>>,
 }
 
 impl<MP: FieldParameters + TwoAdicData> RecursiveDft<MontyField31<MP>> {
     pub fn new(n: usize) -> Self {
-        let res = Self {
-            twiddles: Arc::default(),
-            inv_twiddles: Arc::default(),
-        };
+        let res = Self::default();
         res.update_twiddles(n);
         res
     }
@@ -98,10 +112,10 @@ impl<MP: FieldParameters + TwoAdicData> RecursiveDft<MontyField31<MP>> {
         // As we don't save the twiddles for the final layer where
         // the only twiddle is 1, roots_of_unity_table(fft_len)
         // returns a vector of twiddles of length log_2(fft_len) - 1.
-        // let curr_max_fft_len = 2 << self.twiddles.read().len();
         let need = log2_strict_usize(fft_len);
-        let snapshot = self.twiddles.read().clone();
-        let have = snapshot.len() + 1;
+
+        // Fast path: read lock to check if we already have enough.
+        let have = self.cache.read().twiddles.len() + 1;
         if have >= need {
             return;
         }
@@ -121,31 +135,32 @@ impl<MP: FieldParameters + TwoAdicData> RecursiveDft<MontyField31<MP>> {
                     .collect()
             })
             .collect::<Vec<_>>();
-        // Helper closure to extend a table under its lock.
+
+        // Slow path: acquire write lock and update both tables atomically.
         let have_minus_one = have - 1;
-        let extend_table = |lock: &RwLock<Arc<[Vec<_>]>>, missing: &[Vec<_>]| {
-            let mut w = lock.write();
-            let current_len = w.len();
-            // Double-check if an update is still needed after acquiring the write lock.
-            if (current_len + 1) < need {
-                let mut v = w.to_vec();
-                // Append only the portion needed in case another thread did a partial update.
-                let extend_from = current_len.saturating_sub(have_minus_one);
-                v.extend_from_slice(&missing[extend_from..]);
-                *w = v.into();
-            }
-        };
-        // Atomically update each table. This two-step process is the source of the race condition.
-        extend_table(&self.twiddles, &missing_twiddles);
-        extend_table(&self.inv_twiddles, &missing_inv_twiddles);
+        let mut cache = self.cache.write();
+        let current_len = cache.twiddles.len();
+        // Double-check if an update is still needed after acquiring the write lock.
+        if (current_len + 1) < need {
+            let extend_from = current_len.saturating_sub(have_minus_one);
+
+            let mut tw = cache.twiddles.to_vec();
+            tw.extend_from_slice(&missing_twiddles[extend_from..]);
+
+            let mut inv_tw = cache.inv_twiddles.to_vec();
+            inv_tw.extend_from_slice(&missing_inv_twiddles[extend_from..]);
+
+            cache.twiddles = tw.into();
+            cache.inv_twiddles = inv_tw.into();
+        }
     }
 
     fn get_twiddles(&self) -> Arc<[Vec<MontyField31<MP>>]> {
-        self.twiddles.read().clone()
+        self.cache.read().twiddles.clone()
     }
 
     fn get_inv_twiddles(&self) -> Arc<[Vec<MontyField31<MP>>]> {
-        self.inv_twiddles.read().clone()
+        self.cache.read().inv_twiddles.clone()
     }
 }
 
```
