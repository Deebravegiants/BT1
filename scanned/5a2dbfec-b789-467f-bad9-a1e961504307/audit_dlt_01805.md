# [?] Fix bf.unset(u64::MAX) causing delayed panic on bf.ranges()

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/ref-fvm
Published: 2022-03-29
Source: https://github.com/filecoin-project/ref-fvm/commit/35fc054bcde416098f5a0f46b412ed1ab033556b
Type: security-commit

## Details
Fix bf.unset(u64::MAX) causing delayed panic on bf.ranges()

Detected by rle_encode fuzz target.
Caused by overflow when trying to compute input ranges into difference
operation within `ranges()`.

Signed-off-by: Jakub Sztandera <kubuxu@protocol.ai>

## Patch
### ipld/bitfield/src/lib.rs
```diff
@@ -170,6 +170,9 @@ impl BitField {
 
     /// Removes the bit at a given index from the bit field.
     pub fn unset(&mut self, bit: u64) {
+        if bit == u64::MAX {
+            return;
+        }
         self.set.remove(&bit);
         self.unset.insert(bit);
     }
```

### ipld/bitfield/src/rleplus/mod.rs
```diff
@@ -509,6 +509,20 @@ mod tests {
         assert_eq!(2, last);
     }
 
+    #[test]
+    fn test_unset_max() {
+        // Create any bitfield
+        let ranges: Vec<u64> = vec![0, 1, 2, 3];
+        let iter = ranges_from_bits(ranges);
+        let mut bf = BitField::from_ranges(iter);
+
+        // Unset u64::MAX
+        bf.unset(u64::MAX);
+
+        let last = bf.ranges().last().unwrap();
+        assert_eq!(0..4, last);
+    }
+
     #[test]
     fn test_zero_last() {
         let mut bf = BitField::new();
```
