# [?] Bug 554 - fix stack overflow (#555)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2022-11-02
Source: https://github.com/stellar/rs-soroban-env/commit/a9af5797d3ee41dd123fa2bb620a714319084934
Type: security-commit

## Details
Bug 554 - fix stack overflow (#555)

* Fix stack overflow in im_rc due to non-optimal btree code with large key and value types

* Add tests for map stack overflow in bug #554

## Patch
### soroban-env-host/src/host.rs
```diff
@@ -63,7 +63,7 @@ use self::metered_vector::MeteredVector;
 // Notes on metering: `RollbackPoint` are metered under Frame operations
 #[derive(Clone)]
 pub(crate) struct RollbackPoint {
-    storage: MeteredOrdMap<LedgerKey, Option<LedgerEntry>>,
+    storage: MeteredOrdMap<Box<LedgerKey>, Option<Box<LedgerEntry>>>,
     objects: usize,
 }
 
```

### soroban-env-host/src/host/metered_map.rs
```diff
@@ -43,12 +43,21 @@ impl<K, V> Default for MeteredOrdMap<K, V> {
     }
 }
 
+fn check_size_is_small<T>(name: &str) {
+    let sz = core::mem::size_of::<T>();
+    if sz > 64 {
+        panic!("type '{}' is too big: {}", name, sz);
+    }
+}
+
 impl<K, V> MeteredOrdMap<K, V>
 where
     K: Ord + Clone,
     V: Clone,
 {
     pub fn new(budget: Budget) -> Result<Self, HostError> {
+        check_size_is_small::<K>("key");
+        check_size_is_small::<V>("val");
         budget.charge(CostType::ImMapNew, 1)?;
         Ok(MeteredOrdMap {
             budget,
@@ -57,6 +66,8 @@ where
     }
 
     pub fn from_map(budget: Budget, map: OrdMap<K, V>) -> Result<Self, HostError> {
+        check_size_is_small::<K>("key");
+        check_size_is_small::<V>("val");
         budget.charge(CostType::ImMapNew, 1)?;
         Ok(MeteredOrdMap { budget, map })
     }
```

### soroban-env-host/src/storage.rs
```diff
@@ -42,7 +42,7 @@ pub trait SnapshotSource {
 /// against a suitably fresh [SnapshotSource].
 // Notes on metering: covered by the underneath `MeteredOrdMap`.
 #[derive(Clone, Default)]
-pub struct Footprint(pub MeteredOrdMap<LedgerKey, AccessType>);
+pub struct Footprint(pub MeteredOrdMap<Box<LedgerKey>, AccessType>);
 
 impl Footprint {
     pub fn record_access(&mut self, key: &LedgerKey, ty: AccessType) -> Result<(), HostError> {
@@ -52,14 +52,14 @@ impl Footprint {
                 (AccessType::ReadOnly, AccessType::ReadWrite) => {
                     // The only interesting case is an upgrade
                     // from previously-read-only to read-write.
-                    self.0.insert(key.clone(), ty)?;
+                    self.0.insert(Box::new(key.clone()), ty)?;
                     Ok(())
                 }
                 (AccessType::ReadWrite, AccessType::ReadOnly) => Ok(()),
                 (AccessType::ReadWrite, AccessType::ReadWrite) => Ok(()),
             }
         } else {
-            self.0.insert(key.clone(), ty)?;
+            self.0.insert(Box::new(key.clone()), ty)?;
             Ok(())
         }
     }
@@ -109,7 +109,7 @@ impl Default for FootprintMode {
 pub struct Storage {
     pub footprint: Footprint,
     pub mode: FootprintMode,
-    pub map: MeteredOrdMap<LedgerKey, Option<LedgerEntry>>,
+    pub map: MeteredOrdMap<Box<LedgerKey>, Option<Box<LedgerEntry>>>,
 }
 
 // Notes on metering: all storage operations: `put`, `get`, `del`, `has` are
@@ -120,7 +120,7 @@ impl Storage {
     /// listed in the [Footprint].
     pub fn with_enforcing_footprint_and_map(
         footprint: Footprint,
-        map: MeteredOrdMap<LedgerKey, Option<LedgerEntry>>,
+        map: MeteredOrdMap<Box<LedgerKey>, Option<Box<LedgerEntry>>>,
     ) -> Self {
         Self {
             mode: FootprintMode::Enforcing,
@@ -158,7 +158,8 @@ impl Storage {
                 // In recording mode we treat the map as a cache
                 // that misses read-through to the underlying src.
                 if !self.map.contains_key(key)? {
-                    self.map.insert(key.clone(), Some(src.get(key)?))?;
+                    self.map
+                        .insert(Box::new(key.clone()), Some(Box::new(src.get(key)?)))?;
                 }
             }
             FootprintMode::Enforcing => {
@@ -168,7 +169,7 @@ impl Storage {
         match self.map.get(key)? {
             None => Err(ScHostStorageErrorCode::MissingKeyInGet.into()),
             Some(None) => Err(ScHostStorageErrorCode::GetOnDeletedKey.into()),
-            Some(Some(val)) => Ok(val.clone()),
+            Some(Some(val)) => Ok((**val).clone()),
         }
     }
 
@@ -182,7 +183,8 @@ impl Storage {
                 self.footprint.enforce_access(key, ty)?;
             }
         };
-        self.map.insert(key.clone(), val)?;
+        self.map
+            .insert(Box::new(key.clone()), val.map(|v| Box::new(v)))?;
         Ok(())
     }
 
@@ -282,11 +284,11 @@ mod test_footprint {
             contract_id,
             key: ScVal::I32(0),
         });
-        let om = OrdMap::unit(key.clone(), AccessType::ReadOnly);
+        let om = OrdMap::unit(Box::new(key.clone()), AccessType::ReadOnly);
         let mom = MeteredOrdMap::from_map(budget, om)?;
         let mut fp = Footprint(mom);
         fp.enforce_access(&key, AccessType::ReadOnly)?;
-        fp.0.insert(key.clone(), AccessType::ReadWrite)?;
+        fp.0.insert(Box::new(key.clone()), AccessType::ReadWrite)?;
         fp.enforce_access(&key, AccessType::ReadOnly)?;
         fp.enforce_access(&key, AccessType::ReadWrite)?;
         Ok(())
@@ -316,7 +318,7 @@ mod test_footprint {
             contract_id,
             key: ScVal::I32(0),
         });
-        let om = OrdMap::unit(key.clone(), AccessType::ReadOnly);
+        let om = OrdMap::unit(Box::new(key.clone()), AccessType::ReadOnly);
         let mom = MeteredOrdMap::from_map(budget, om)?;
         let mut fp = Footprint(mom);
         let res = fp.enforce_access(&key, AccessType::ReadWrite);
```

### soroban-env-host/src/test/account.rs
```diff
@@ -22,7 +22,7 @@ fn check_account_exists() -> Result<(), HostError> {
     footprint.record_access(&lk1, AccessType::ReadOnly).unwrap();
 
     let mut map = im_rc::OrdMap::default();
-    map.insert(lk0, Some(le0));
+    map.insert(Box::new(lk0), Some(Box::new(le0)));
     let storage = Storage::with_enforcing_footprint_and_map(
         footprint,
         MeteredOrdMap {
```

### soroban-env-host/src/test/bytes.rs
```diff
@@ -188,7 +188,7 @@ fn linear_memory_operations() -> Result<(), HostError> {
         }),
         ext: LedgerEntryExt::V0,
     };
-    let map = OrdMap::unit(storage_key.clone(), Some(le));
+    let map = OrdMap::unit(Box::new(storage_key.clone()), Some(Box::new(le)));
     let mut footprint = Footprint::default();
     footprint.record_access(&storage_key, AccessType::ReadOnly)?;
 
```

### soroban-env-host/src/test/map.rs
```diff
@@ -1,3 +1,8 @@
+use im_rc::OrdMap;
+use soroban_env_common::xdr::{
+    AccountId, LedgerEntry, LedgerKey, LedgerKeyAccount, PublicKey, Uint256,
+};
+
 use crate::{
     xdr::{ScMap, ScMapEntry, ScObject, ScVal, ScVec},
     CheckedEnv, Host, HostError, RawVal, RawValConvertible, Status, Symbol,
@@ -221,3 +226,59 @@ fn map_values() -> Result<(), HostError> {
 
     Ok(())
 }
+
+#[test]
+#[ignore = "aborts with a stack overflow"]
+fn map_stack_overflow_63356_big_keys_and_vals() {
+    let mut map: OrdMap<LedgerKey, Option<LedgerEntry>> = OrdMap::new();
+    for a in 0..=255 {
+        for b in 0..=255 {
+            let mut k: [u8; 32] = [0; 32];
+            k[0] = a;
+            k[1] = b;
+            let pk = PublicKey::PublicKeyTypeEd25519(Uint256(k));
+            let key = LedgerKey::Account(LedgerKeyAccount {
+                account_id: AccountId(pk),
+            });
+            map.insert(key, None);
+        }
+    }
+}
+
+#[test]
+fn map_stack_no_overflow_65536_boxed_keys_and_vals() {
+    let mut map: OrdMap<Box<LedgerKey>, Option<Box<LedgerEntry>>> = OrdMap::new();
+    for a in 0..=255 {
+        for b in 0..=255 {
+            let mut k: [u8; 32] = [0; 32];
+            k[0] = a;
+            k[1] = b;
+            let pk = PublicKey::PublicKeyTypeEd25519(Uint256(k));
+            let key = LedgerKey::Account(LedgerKeyAccount {
+                account_id: AccountId(pk),
+            });
+            map.insert(Box::new(key), None);
+        }
+    }
+}
+
+#[test]
+#[ignore = "runs for too long on debug builds"]
+fn map_stack_no_overflow_16777216_boxed_keys_and_vals() {
+    let mut map: OrdMap<Box<LedgerKey>, Option<Box<LedgerEntry>>> = OrdMap::new();
+    for a in 0..=255 {
+        for b in 0..=255 {
+            for c in 0..=255 {
+                let mut k: [u8; 32] = [0; 32];
+                k[0] = a;
+                k[1] = b;
+                k[2] = c;
+                let pk = PublicKey::PublicKeyTypeEd25519(Uint256(k));
+                let key = LedgerKey::Account(LedgerKeyAccount {
+                    account_id: AccountId(pk),
+                });
+                map.insert(Box::new(key), None);
+            }
+        }
+    }
+}
```

### soroban-env-host/src/test/util.rs
```diff
@@ -89,7 +89,7 @@ impl Host {
                 }),
                 ext: LedgerEntryExt::V0,
             };
-            map.insert(storage_key.clone(), Some(le));
+            map.insert(Box::new(storage_key.clone()), Some(Box::new(le)));
             footprint
                 .record_access(&storage_key, AccessType::ReadOnly)
                 .unwrap();
```
