# [?] Fix stack overflow crash + more memoization

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2023-02-12
Source: https://github.com/casper-network/casper-node/commit/4520b6b59048eb5add44534a501ffda3a908d977
Type: security-commit

## Details
Fix stack overflow crash + more memoization

## Patch
### node/src/components/consensus/highway_core/highway/vertex.rs
```diff
@@ -140,18 +140,18 @@ impl<C: Context> Vertex<C> {
 
 #[cfg(test)]
 mod specimen_support {
+    use super::{
+        Dependency, DependencyDiscriminants, Endorsements, HashedWireUnit, Ping, SignedEndorsement,
+        SignedWireUnit, Vertex, VertexDiscriminants, WireUnit,
+    };
     use crate::{
         components::consensus::ClContext,
         testing::specimen::{
             btree_set_distinct_from_prop, largest_variant, vec_prop_specimen, LargestSpecimen,
             SizeEstimator,
         },
     };
-
-    use super::{
-        Dependency, DependencyDiscriminants, Endorsements, HashedWireUnit, Ping, SignedEndorsement,
-        SignedWireUnit, Vertex, VertexDiscriminants, WireUnit,
-    };
+    use std::{any::TypeId, cell::RefCell, collections::HashMap};
 
     impl LargestSpecimen for Vertex<ClContext> {
         fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self {
@@ -234,10 +234,21 @@ mod specimen_support {
 
     impl LargestSpecimen for HashedWireUnit<ClContext> {
         fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self {
-            HashedWireUnit {
-                hash: LargestSpecimen::largest_specimen(estimator),
-                wire_unit: LargestSpecimen::largest_specimen(estimator),
+            thread_local! {
+                static MEMOIZED: RefCell<HashMap<TypeId, HashedWireUnit<ClContext>>> = Default::default();
             }
+
+            MEMOIZED.with(|cache| {
+                cache
+                    .try_borrow_mut()
+                    .expect("cannot borrow the memoization cache")
+                    .entry(TypeId::of::<E>())
+                    .or_insert_with(|| HashedWireUnit {
+                        hash: LargestSpecimen::largest_specimen(estimator),
+                        wire_unit: LargestSpecimen::largest_specimen(estimator),
+                    })
+                    .clone()
+            })
         }
     }
 
```

### node/src/components/consensus/highway_core/state/panorama.rs
```diff
@@ -250,17 +250,31 @@ mod specimen_support {
         components::consensus::ClContext,
         testing::specimen::{largest_variant, LargestSpecimen, SizeEstimator},
     };
+    use std::{any::TypeId, cell::RefCell, collections::HashMap};
 
     use super::{Observation, ObservationDiscriminants};
 
     impl LargestSpecimen for Observation<ClContext> {
         fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self {
-            largest_variant(estimator, |variant| match variant {
-                ObservationDiscriminants::None => Observation::None,
-                ObservationDiscriminants::Correct => {
-                    Observation::Correct(LargestSpecimen::largest_specimen(estimator))
-                }
-                ObservationDiscriminants::Faulty => Observation::Faulty,
+            thread_local! {
+                static MEMOIZED: RefCell<HashMap<TypeId, Observation<ClContext>>> = Default::default();
+            }
+
+            MEMOIZED.with(|cache| {
+                cache
+                    .try_borrow_mut()
+                    .expect("cannot borrow the memoization cache")
+                    .entry(TypeId::of::<E>())
+                    .or_insert_with(|| {
+                        largest_variant(estimator, |variant| match variant {
+                            ObservationDiscriminants::None => Observation::None,
+                            ObservationDiscriminants::Correct => {
+                                Observation::Correct(LargestSpecimen::largest_specimen(estimator))
+                            }
+                            ObservationDiscriminants::Faulty => Observation::Faulty,
+                        })
+                    })
+                    .clone()
             })
         }
     }
```

### node/src/components/consensus/protocols/zug.rs
```diff
@@ -2249,10 +2249,10 @@ where
 
 #[cfg(test)]
 mod specimen_support {
-    use std::{collections::BTreeSet, sync::Arc};
+    use std::{any::TypeId, cell::RefCell, collections::BTreeSet, collections::HashMap};
 
     use crate::{
-        components::consensus::{cl_context::Keypair, utils::ValidatorIndex, ClContext},
+        components::consensus::{utils::ValidatorIndex, ClContext},
         testing::specimen::{
             btree_map_distinct_from_prop, btree_set_distinct_from_prop, largest_variant,
             vec_prop_specimen, LargeUniqueSequence, LargestSpecimen, SizeEstimator,
@@ -2368,17 +2368,29 @@ mod specimen_support {
 
     impl LargestSpecimen for Content<ClContext> {
         fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self {
-            largest_variant::<Self, ContentDiscriminants, _, _>(
-                estimator,
-                |variant| match variant {
-                    ContentDiscriminants::Echo => {
-                        Content::Echo(LargestSpecimen::largest_specimen(estimator))
-                    }
-                    ContentDiscriminants::Vote => {
-                        Content::Vote(LargestSpecimen::largest_specimen(estimator))
-                    }
-                },
-            )
+            thread_local! {
+                static MEMOIZED: RefCell<HashMap<TypeId, Content<ClContext>>> = Default::default();
+            }
+
+            MEMOIZED.with(|cache| {
+                cache
+                    .try_borrow_mut()
+                    .expect("cannot borrow the memoization cache")
+                    .entry(TypeId::of::<E>())
+                    .or_insert_with(|| {
+                        largest_variant::<Self, ContentDiscriminants, _, _>(estimator, |variant| {
+                            match variant {
+                                ContentDiscriminants::Echo => {
+                                    Content::Echo(LargestSpecimen::largest_specimen(estimator))
+                                }
+                                ContentDiscriminants::Vote => {
+                                    Content::Vote(LargestSpecimen::largest_specimen(estimator))
+                                }
+                            }
+                        })
+                    })
+                    .clone()
+            })
         }
     }
 }
```

### node/src/components/fetcher/fetch_response.rs
```diff
@@ -53,13 +53,13 @@ mod specimen_support {
             largest_variant::<Self, FetchResponseDiscriminants, _, _>(estimator, |variant| {
                 match variant {
                     FetchResponseDiscriminants::Fetched => {
-                        LargestSpecimen::largest_specimen(estimator)
+                        FetchResponse::Fetched(LargestSpecimen::largest_specimen(estimator))
                     }
                     FetchResponseDiscriminants::NotFound => {
-                        LargestSpecimen::largest_specimen(estimator)
+                        FetchResponse::NotFound(LargestSpecimen::largest_specimen(estimator))
                     }
                     FetchResponseDiscriminants::NotProvided => {
-                        LargestSpecimen::largest_specimen(estimator)
+                        FetchResponse::NotProvided(LargestSpecimen::largest_specimen(estimator))
                     }
                 }
             })
```

### node/src/components/network/message.rs
```diff
@@ -542,10 +542,6 @@ mod tests {
                 _ => None,
             }
         }
-
-        fn key() -> &'static str {
-            "NetworkMessageEstimator"
-        }
     }
 
     #[test]
```

### node/src/testing/specimen.rs
```diff
@@ -5,11 +5,13 @@
 
 use core::convert::TryInto;
 use std::{
+    any::TypeId,
+    cell::RefCell,
     collections::{BTreeMap, BTreeSet, HashMap},
     convert::TryFrom,
     iter::FromIterator,
     net::{Ipv6Addr, SocketAddr, SocketAddrV6},
-    sync::{Arc, Mutex},
+    sync::Arc,
 };
 
 use casper_execution_engine::core::engine_state::{
@@ -23,7 +25,6 @@ use casper_types::{
     SecretKey, SemVer, SignatureDiscriminants, TimeDiff, Timestamp, KEY_HASH_LENGTH, U512,
 };
 use either::Either;
-use once_cell::sync::Lazy;
 use serde::Serialize;
 use strum::IntoEnumIterator;
 
@@ -45,7 +46,7 @@ use crate::{
 pub(crate) const HIGHEST_UNICODE_CODEPOINT: char = '\u{10FFFF}';
 
 /// Given a specific type instance, estimates its serialized size.
-pub(crate) trait SizeEstimator {
+pub(crate) trait SizeEstimator: 'static {
     /// Estimate the serialized size of a value.
     fn estimate<T: Serialize>(&self, val: &T) -> usize;
 
@@ -77,16 +78,13 @@ pub(crate) trait SizeEstimator {
             )
         })
     }
-
-    /// An identifier for this specific estimator, used for memoization.
-    fn key() -> &'static str;
 }
 
 /// Supports returning a maximum size specimen.
 ///
 /// "Maximum size" refers to the instance that uses the highest amount of memory and is also most
 /// likely to have the largest representation when serialized.
-pub(crate) trait LargestSpecimen {
+pub(crate) trait LargestSpecimen: Sized {
     /// Returns the largest possible specimen for this type.
     fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self;
 }
@@ -356,39 +354,74 @@ impl LargestSpecimen for SemVer {
     }
 }
 
-//static RNG: once_cell::sync::Lazy<std::sync::Mutex<TestRng>> =
-//    once_cell::sync::Lazy::new(|| std::sync::Mutex::new(TestRng::new()));
+thread_local! {
+    static RNG: once_cell::sync::Lazy<RefCell<TestRng>> =
+        once_cell::sync::Lazy::new(|| RefCell::new(TestRng::new()));
+}
 
 impl LargestSpecimen for PublicKey {
     fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self {
-        PublicKey::system()
-        //largest_random_public_key(
-        //    estimator,
-        //    &mut RNG.lock().expect("the test rng to be acquired"),
-        //)
+        thread_local! {
+            static MEMOIZED: RefCell<HashMap<TypeId, PublicKey>> = Default::default();
+        }
+
+        MEMOIZED.with(|cache| {
+            cache
+                .try_borrow_mut()
+                .expect("cannot borrow the memoization cache")
+                .entry(TypeId::of::<E>())
+                .or_insert_with(|| {
+                    RNG.with(|rng| {
+                        largest_random_public_key(
+                            estimator,
+                            &mut rng.try_borrow_mut().expect("the test rng to be acquired"),
+                        )
+                    })
+                })
+                .clone()
+        })
     }
 }
 
-//fn largest_random_public_key<E: SizeEstimator>(estimator: &E, rng: &mut TestRng) -> PublicKey {
-//    largest_variant::<PublicKey, PublicKeyDiscriminants, _, _>(estimator, move |variant| {
-//        match variant {
-//            PublicKeyDiscriminants::System => PublicKey::system(),
-//            PublicKeyDiscriminants::Ed25519 => PublicKey::random_ed25519(rng),
-//            PublicKeyDiscriminants::Secp256k1 => PublicKey::random_secp256k1(rng),
-//        }
-//    })
-//}
+fn largest_random_public_key<E: SizeEstimator>(estimator: &E, rng: &mut TestRng) -> PublicKey {
+    println!("largest_random_public_key");
+    largest_variant::<PublicKey, PublicKeyDiscriminants, _, _>(estimator, move |variant| {
+        match variant {
+            PublicKeyDiscriminants::System => PublicKey::system(),
+            PublicKeyDiscriminants::Ed25519 => PublicKey::random_ed25519(rng),
+            PublicKeyDiscriminants::Secp256k1 => PublicKey::random_secp256k1(rng),
+        }
+    })
+}
 
 impl<E> LargeUniqueSequence<E> for PublicKey
 where
     E: SizeEstimator,
 {
     fn large_unique_sequence(estimator: &E, count: usize) -> BTreeSet<Self> {
-        //let rng = &mut RNG.lock().expect("the test rng to be acquired");
-        //(0..count)
-        //    .map(move |_| largest_random_public_key(estimator, rng))
-        //    .collect()
-        (0..count).map(|_| PublicKey::system()).collect()
+        thread_local! {
+            static MEMOIZED: RefCell<HashMap<(TypeId, usize), BTreeSet<PublicKey>>> = Default::default();
+        }
+
+        MEMOIZED.with(|cache| {
+            cache
+                .try_borrow_mut()
+                .expect("cannot borrow the memoization cache")
+                .entry((TypeId::of::<E>(), count))
+                .or_insert_with(|| {
+                    RNG.with(|rng| {
+                        (0..count)
+                            .map(move |_| {
+                                largest_random_public_key(
+                                    estimator,
+                                    &mut rng.try_borrow_mut().expect("the test rng to be acquired"),
+                                )
+                            })
+                            .collect()
+                    })
+                })
+                .clone()
+        })
     }
 }
 
@@ -403,30 +436,33 @@ where
 
 impl LargestSpecimen for Signature {
     fn largest_specimen<E: SizeEstimator>(estimator: &E) -> Self {
-        static MEMOIZED: Lazy<Mutex<HashMap<&'static str, Signature>>> =
-            Lazy::new(|| Mutex::new(HashMap::new()));
-
-        MEMOIZED
-            .lock()
-            .expect("memoized signature specimen cache disappeared")
-            .entry(E::key())
-            .or_insert_with(|| {
-                let ed25519_sec = &SecretKey::generate_ed25519().expect("a correct secret");
-                let secp256k1_sec = &SecretKey::generate_secp256k1().expect("a correct secret");
-
-                largest_variant::<Self, SignatureDiscriminants, _, _>(estimator, |variant| {
-                    match variant {
-                        SignatureDiscriminants::System => Signature::system(),
-                        SignatureDiscriminants::Ed25519 => {
-                            sign([0_u8], ed25519_sec, &ed25519_sec.into())
-                        }
-                        SignatureDiscriminants::Secp256k1 => {
-                            sign([0_u8], secp256k1_sec, &secp256k1_sec.into())
+        thread_local! {
+            static MEMOIZED: RefCell<HashMap<TypeId, Signature>> = Default::default();
+        }
+
+        MEMOIZED.with(|cache| {
+            cache
+                .try_borrow_mut()
+                .expect("cannot borrow the memoization cache")
+                .entry(TypeId::of::<E>())
+                .or_insert_with(|| {
+                    let ed25519_sec = &SecretKey::generate_ed25519().expect("a correct secret");
+                    let secp256k1_sec = &SecretKey::generate_secp256k1().expect("a correct secret");
+
+                    largest_variant::<Self, SignatureDiscriminants, _, _>(estimator, |variant| {
+                        match variant {
+                            SignatureDiscriminants::System => Signature::system(),
+                            SignatureDiscriminants::Ed25519 => {
+                                sign([0_u8], ed25519_sec, &ed25519_sec.into())
+                            }
+                            SignatureDiscriminants::Secp256k1 => {
+                                sign([0_u8], secp256k1_sec, &secp256k1_sec.into())
+                            }
                         }
-                    }
+                    })
                 })
-            })
-            .clone()
+                .clone()
+        })
     }
 }
 
```
