# [?] Fix a deadlock when cached item is not in cache (#85)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2022-12-04
Source: https://github.com/kaspanet/rusty-kaspa/commit/7ac043f67329983e26b496ec5135781bd4319cae
Type: security-commit

## Details
Fix a deadlock when cached item is not in cache (#85)

## Patch
### consensus/src/model/stores/database/item.rs
```diff
@@ -23,8 +23,9 @@ impl<T> CachedDbItem<T> {
         T: Clone + DeserializeOwned,
     {
         if let Some(item) = self.cached_item.read().clone() {
-            Ok(item)
-        } else if let Some(slice) = self.db.get_pinned(self.key)? {
+            return Ok(item);
+        }
+        if let Some(slice) = self.db.get_pinned(self.key)? {
             let item: T = bincode::deserialize(&slice)?;
             *self.cached_item.write() = Some(item.clone());
             Ok(item)
```
