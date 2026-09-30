# [?] Merge rust-bitcoin/rust-bitcoin#4847: Fix overflows in `Weight` and add fuzz target

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-08-22
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/911e1439f959c9cb3dc1e3d474eb431360a422eb
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#4847: Fix overflows in `Weight` and add fuzz target

aa086a0a01bcae252de39a461de9286b3b9adee8 Fix overflow bug in `Weight` constructors (Shing Him Ng)
b762f746ca90dea31838a3d0c4096ec9e09a08b4 Add fuzz target for `Weight` (Shing Him Ng)
e11d3ed46f7e0a066f77e55d001178502a0340e4 Update `from_vb_unchecked` to use constant (Shing Him Ng)
e815d32eec8313ea394a630d694f1515e104ee4c Bump version of workflow in fuzz file generation (Shing Him Ng)

Pull request description:

  Pulling on the same thread from #4838, I started looking into `units` where a similar bugs may have happened and found a few for `Weight`. Found a few instances of the overflow bug in a few constructors so fixing them here


ACKs for top commit:
  tcharding:
    ACK aa086a0a01bcae252de39a461de9286b3b9adee8
  apoelstra:
    ACK aa086a0a01bcae252de39a461de9286b3b9adee8; successfully ran local tests


Tree-SHA512: 8a586ed3fdc6bd27c86ff218c3ae4ac79d51a43712af4af85d5caea8252b730cdceed967c8eb13ffd05e010404478de195dd3a4759a1e76d3b60a3880e555b36

## Patch
### .github/workflows/cron-daily-fuzz.yml
```diff
@@ -35,6 +35,7 @@ jobs:
           hashes_sha256,
           hashes_sha512,
           hashes_sha512_256,
+          units_arbitrary_weight,
           units_parse_amount,
         ]
     steps:
```

### fuzz/Cargo.toml
```diff
@@ -89,6 +89,10 @@ path = "fuzz_targets/hashes/sha512.rs"
 name = "hashes_sha512_256"
 path = "fuzz_targets/hashes/sha512_256.rs"
 
+[[bin]]
+name = "units_arbitrary_weight"
+path = "fuzz_targets/units/arbitrary_weight.rs"
+
 [[bin]]
 name = "units_parse_amount"
 path = "fuzz_targets/units/parse_amount.rs"
```

### fuzz/fuzz_targets/units/arbitrary_weight.rs
```diff
@@ -0,0 +1,87 @@
+use arbitrary::{Arbitrary, Unstructured};
+use honggfuzz::fuzz;
+use bitcoin::Weight;
+
+fn do_test(data: &[u8]) {
+    let mut u = Unstructured::new(data);
+    let w = Weight::arbitrary(&mut u);
+
+    if let Ok(weight) = w {
+        weight.to_wu();
+        weight.to_kwu_ceil();
+        weight.to_kwu_floor();
+        weight.to_vbytes_ceil();
+        weight.to_vbytes_floor();
+
+        // Operations that take u64 as the rhs
+        for operation in [Weight::checked_mul, Weight::checked_div] {
+            if let Ok(val) = u.arbitrary() {
+                let _ = operation(weight, val);
+            } else {
+                return;
+            }
+        }
+
+        // Operations that take Weight as the rhs
+        for operation in [Weight::checked_add, Weight::checked_sub] {
+            if let Ok(val) = u.arbitrary() {
+                let _ = operation(weight, val);
+            } else {
+                return;
+            }
+        }
+    }
+
+    // Constructors that return a Weight
+    for constructor in [Weight::from_wu, Weight::from_witness_data_size,  Weight::from_non_witness_data_size] {
+        if let Ok(val) = u.arbitrary() {
+            constructor(val);
+        } else {
+            return;
+        }
+    }
+
+    // Constructors that return an Option<Weight>
+    for constructor in [Weight::from_vb, Weight::from_kwu] {
+        if let Ok(val) = u.arbitrary() {
+            constructor(val);
+        } else {
+            return;
+        }
+    }
+}
+
+fn main() {
+    loop {
+        fuzz!(|data| {
+            do_test(data);
+        });
+    }
+}
+
+#[cfg(all(test, fuzzing))]
+mod tests {
+    fn extend_vec_from_hex(hex: &str, out: &mut Vec<u8>) {
+        let mut b = 0;
+        for (idx, c) in hex.as_bytes().iter().enumerate() {
+            b <<= 4;
+            match *c {
+                b'A'..=b'F' => b |= c - b'A' + 10,
+                b'a'..=b'f' => b |= c - b'a' + 10,
+                b'0'..=b'9' => b |= c - b'0',
+                _ => panic!("Bad hex"),
+            }
+            if (idx & 1) == 1 {
+                out.push(b);
+                b = 0;
+            }
+        }
+    }
+
+    #[test]
+    fn duplicate_crash() {
+        let mut a = Vec::new();
+        extend_vec_from_hex("00", &mut a);
+        super::do_test(&a);
+    }
+}
```

### fuzz/generate-files.sh
```diff
@@ -102,7 +102,7 @@ $(for name in $(listTargetNames); do echo "          $name,"; done)
     runs-on: ubuntu-24.04
     steps:
       - uses: actions/checkout@v4
-      - uses: actions/download-artifact@v4
+      - uses: actions/download-artifact@v5
       - name: Display structure of downloaded files
         run: ls -R
       - run: find executed_* -type f -exec cat {} + | sort > executed
```

### units/src/weight.rs
```diff
@@ -91,7 +91,7 @@ impl Weight {
     }
 
     /// Constructs a new [`Weight`] from virtual bytes without an overflow check.
-    pub const fn from_vb_unchecked(vb: u64) -> Self { Weight::from_wu(vb * 4) }
+    pub const fn from_vb_unchecked(vb: u64) -> Self { Weight::from_wu(vb * Self::WITNESS_SCALE_FACTOR) }
 
     /// Constructs a new [`Weight`] from witness size.
     pub const fn from_witness_data_size(witness_size: u64) -> Self { Weight::from_wu(witness_size) }
@@ -105,14 +105,14 @@ impl Weight {
     pub const fn to_kwu_floor(self) -> u64 { self.to_wu() / 1000 }
 
     /// Converts to kilo weight units rounding up.
-    pub const fn to_kwu_ceil(self) -> u64 { (self.to_wu() + 999) / 1000 }
+    pub const fn to_kwu_ceil(self) -> u64 { self.to_wu().saturating_add(999) / 1000 }
 
     /// Converts to vB rounding down.
     pub const fn to_vbytes_floor(self) -> u64 { self.to_wu() / Self::WITNESS_SCALE_FACTOR }
 
     /// Converts to vB rounding up.
     pub const fn to_vbytes_ceil(self) -> u64 {
-        (self.to_wu() + Self::WITNESS_SCALE_FACTOR - 1) / Self::WITNESS_SCALE_FACTOR
+        self.to_wu().saturating_add(Self::WITNESS_SCALE_FACTOR - 1) / Self::WITNESS_SCALE_FACTOR
     }
 
     /// Checked addition.
@@ -387,6 +387,7 @@ mod tests {
     fn to_kwu_ceil() {
         assert_eq!(Weight::from_wu(1_000).to_kwu_ceil(), 1);
         assert_eq!(Weight::from_wu(1_001).to_kwu_ceil(), 2);
+        assert_eq!(Weight::MAX.to_kwu_ceil(), u64::MAX / 1_000);
     }
 
     #[test]
@@ -399,6 +400,7 @@ mod tests {
     fn to_vb_ceil() {
         assert_eq!(Weight::from_wu(4).to_vbytes_ceil(), 1);
         assert_eq!(Weight::from_wu(5).to_vbytes_ceil(), 2);
+        assert_eq!(Weight::MAX.to_vbytes_ceil(), u64::MAX / Weight::WITNESS_SCALE_FACTOR);
     }
 
     #[test]
```
