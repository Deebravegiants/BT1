# [?] fix(fuzz): prevent int strategy to overflow when complicate (#7447)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-03-20
Source: https://github.com/foundry-rs/foundry/commit/a7f1b3b907b76454eb9e315992b8140b6d292e00
Type: security-commit

## Details
fix(fuzz): prevent int strategy to overflow when complicate (#7447)

## Patch
### crates/evm/fuzz/src/strategies/int.rs
```diff
@@ -67,7 +67,11 @@ impl ValueTree for IntValueTree {
             return false
         }
 
-        self.lo = self.curr + if self.hi.is_negative() { I256::MINUS_ONE } else { I256::ONE };
+        self.lo = if self.curr != I256::MIN && self.curr != I256::MAX {
+            self.curr + if self.hi.is_negative() { I256::MINUS_ONE } else { I256::ONE }
+        } else {
+            self.curr
+        };
 
         self.reposition()
     }
@@ -192,3 +196,25 @@ impl Strategy for IntStrategy {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use crate::strategies::int::IntValueTree;
+    use alloy_primitives::I256;
+    use proptest::strategy::ValueTree;
+
+    #[test]
+    fn test_int_tree_complicate_should_not_overflow() {
+        let mut int_tree = IntValueTree::new(I256::MAX, false);
+        assert_eq!(int_tree.hi, I256::MAX);
+        assert_eq!(int_tree.curr, I256::MAX);
+        int_tree.complicate();
+        assert_eq!(int_tree.lo, I256::MAX);
+
+        let mut int_tree = IntValueTree::new(I256::MIN, false);
+        assert_eq!(int_tree.hi, I256::MIN);
+        assert_eq!(int_tree.curr, I256::MIN);
+        int_tree.complicate();
+        assert_eq!(int_tree.lo, I256::MIN);
+    }
+}
```

### crates/evm/fuzz/src/strategies/uint.rs
```diff
@@ -167,3 +167,19 @@ impl Strategy for UintStrategy {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use crate::strategies::uint::UintValueTree;
+    use alloy_primitives::U256;
+    use proptest::strategy::ValueTree;
+
+    #[test]
+    fn test_uint_tree_complicate_max() {
+        let mut uint_tree = UintValueTree::new(U256::MAX, false);
+        assert_eq!(uint_tree.hi, U256::MAX);
+        assert_eq!(uint_tree.curr, U256::MAX);
+        uint_tree.complicate();
+        assert_eq!(uint_tree.lo, U256::MIN);
+    }
+}
```
