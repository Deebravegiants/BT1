# [?] fix share verify panic (#12959)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-04-22
Source: https://github.com/aptos-labs/aptos-core/commit/30ce450f522ee0b28fa0ea29c9789193c3c30f61
Type: security-commit

## Details
fix share verify panic (#12959)

## Patch
### consensus/src/rand/rand_gen/types.rs
```diff
@@ -1,7 +1,7 @@
 // Copyright © Aptos Foundation
 // SPDX-License-Identifier: Apache-2.0
 
-use anyhow::{bail, ensure};
+use anyhow::{anyhow, bail, ensure};
 use aptos_consensus_types::common::{Author, Round};
 use aptos_crypto::bls12381::Signature;
 use aptos_crypto_derive::{BCSCryptoHash, CryptoHasher};
@@ -59,7 +59,7 @@ impl TShare for Share {
             .validator
             .address_to_validator_index()
             .get(author)
-            .unwrap();
+            .ok_or_else(|| anyhow!("Share::verify failed with unknown author"))?;
         let maybe_apk = &rand_config.keys.certified_apks[index];
         if let Some(apk) = maybe_apk.get() {
             WVUF::verify_share(
```
