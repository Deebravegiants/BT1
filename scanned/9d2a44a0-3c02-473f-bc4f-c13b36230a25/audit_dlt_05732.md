# [?] fix(chain): Return errors instead of panicking in methods for `Height`s (#7591)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-09-21
Source: https://github.com/ZcashFoundation/zebra/commit/daee5e5fcd738a4675369a9281a72eb764222c7f
Type: security-commit

## Details
fix(chain): Return errors instead of panicking in methods for `Height`s (#7591)

* Return errors instead of panicking

* Apply suggestions from code review

Co-authored-by: teor <teor@riseup.net>

* Turn `unwrap`s into `expect`s

* Refactor the error messages

---------

Co-authored-by: teor <teor@riseup.net>

## Patch
### zebra-chain/src/block/height.rs
```diff
@@ -1,6 +1,7 @@
 //! Block height.
 
 use std::ops::{Add, Sub};
+use thiserror::Error;
 
 use crate::{serialization::SerializationError, BoxError};
 
@@ -24,6 +25,14 @@ pub mod json_conversion;
 #[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
 pub struct Height(pub u32);
 
+#[derive(Error, Debug)]
+pub enum HeightError {
+    #[error("The resulting height would overflow Height::MAX.")]
+    Overflow,
+    #[error("The resulting height would underflow Height::MIN.")]
+    Underflow,
+}
+
 impl std::str::FromStr for Height {
     type Err = SerializationError;
     fn from_str(s: &str) -> Result<Self, Self::Err> {
@@ -72,8 +81,8 @@ impl Height {
     ///
     /// - If the current height is at its maximum.
     // TODO Return an error instead of panicking #7263.
-    pub fn next(self) -> Self {
-        (self + 1).expect("Height should not be at its maximum.")
+    pub fn next(self) -> Result<Self, HeightError> {
+        (self + 1).ok_or(HeightError::Overflow)
     }
 
     /// Returns the previous [`Height`].
@@ -82,8 +91,8 @@ impl Height {
     ///
     /// - If the current height is at its minimum.
     // TODO Return an error instead of panicking #7263.
-    pub fn previous(self) -> Self {
-        (self - 1).expect("Height should not be at its minimum.")
+    pub fn previous(self) -> Result<Self, HeightError> {
+        (self - 1).ok_or(HeightError::Underflow)
     }
 
     /// Returns `true` if the [`Height`] is at its minimum.
```

### zebra-state/src/service/finalized_state/disk_format/upgrade/add_subtrees.rs
```diff
@@ -365,7 +365,12 @@ fn check_sapling_subtrees(db: &ZebraDb) -> Result<(), &'static str> {
         }
         // Check that the final note has a greater subtree index if it didn't complete a subtree.
         else {
-            let Some(prev_tree) = db.sapling_tree_by_height(&subtree.end.previous()) else {
+            let prev_height = subtree
+                .end
+                .previous()
+                .expect("Note commitment subtrees should not end at the minimal height.");
+
+            let Some(prev_tree) = db.sapling_tree_by_height(&prev_height) else {
                 result = Err("missing note commitment tree below subtree completion height");
                 error!(?result, ?subtree.end);
                 continue;
@@ -477,7 +482,12 @@ fn check_orchard_subtrees(db: &ZebraDb) -> Result<(), &'static str> {
         }
         // Check that the final note has a greater subtree index if it didn't complete a subtree.
         else {
-            let Some(prev_tree) = db.orchard_tree_by_height(&subtree.end.previous()) else {
+            let prev_height = subtree
+                .end
+                .previous()
+                .expect("Note commitment subtrees should not end at the minimal height.");
+
+            let Some(prev_tree) = db.orchard_tree_by_height(&prev_height) else {
                 result = Err("missing note commitment tree below subtree completion height");
                 error!(?result, ?subtree.end);
                 continue;
```

### zebra-state/src/service/non_finalized_state/chain.rs
```diff
@@ -556,7 +556,12 @@ impl Chain {
         // Don't add a new tree unless it differs from the previous one or there's no previous tree.
         if height.is_min()
             || self
-                .sprout_tree(height.previous().into())
+                .sprout_tree(
+                    height
+                        .previous()
+                        .expect("Already checked for underflow.")
+                        .into(),
+                )
                 .map_or(true, |prev_tree| prev_tree != tree)
         {
             assert_eq!(
@@ -640,7 +645,9 @@ impl Chain {
         // it will always violate the invariant. We restore the invariant by storing the highest
         // (rightmost) removed tree just above `height` if there is no tree at that height.
         if !self.is_empty() && height < self.non_finalized_tip_height() {
-            let next_height = height.next();
+            let next_height = height
+                .next()
+                .expect("Zebra should never reach the max height in normal operation.");
 
             if self.sprout_trees_by_height.get(&next_height).is_none() {
                 // TODO: Use `try_insert` once it stabilises.
@@ -754,7 +761,12 @@ impl Chain {
         // Don't add a new tree unless it differs from the previous one or there's no previous tree.
         if height.is_min()
             || self
-                .sapling_tree(height.previous().into())
+                .sapling_tree(
+                    height
+                        .previous()
+                        .expect("Already checked for underflow.")
+                        .into(),
+                )
                 .map_or(true, |prev_tree| prev_tree != tree)
         {
             assert_eq!(
@@ -834,7 +846,9 @@ impl Chain {
         // it will always violate the invariant. We restore the invariant by storing the highest
         // (rightmost) removed tree just above `height` if there is no tree at that height.
         if !self.is_empty() && height < self.non_finalized_tip_height() {
-            let next_height = height.next();
+            let next_height = height
+                .next()
+                .expect("Zebra should never reach the max height in normal operation.");
 
             if self.sapling_trees_by_height.get(&next_height).is_none() {
                 // TODO: Use `try_insert` once it stabilises.
@@ -954,7 +968,12 @@ impl Chain {
         // Don't add a new tree unless it differs from the previous one or there's no previous tree.
         if height.is_min()
             || self
-                .orchard_tree(height.previous().into())
+                .orchard_tree(
+                    height
+                        .previous()
+                        .expect("Already checked for underflow.")
+                        .into(),
+                )
                 .map_or(true, |prev_tree| prev_tree != tree)
         {
             assert_eq!(
@@ -1034,7 +1053,9 @@ impl Chain {
         // it will always violate the invariant. We restore the invariant by storing the highest
         // (rightmost) removed tree just above `height` if there is no tree at that height.
         if !self.is_empty() && height < self.non_finalized_tip_height() {
-            let next_height = height.next();
+            let next_height = height
+                .next()
+                .expect("Zebra should never reach the max height in normal operation.");
 
             if self.orchard_trees_by_height.get(&next_height).is_none() {
                 // TODO: Use `try_insert` once it stabilises.
```
