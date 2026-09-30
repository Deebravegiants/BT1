# [?] fix: panic in WalletSigner::from_private_key (#8052)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-06-04
Source: https://github.com/foundry-rs/foundry/commit/1c6bd3274430b96ea5c0c1f6bf81bb68912e9813
Type: security-commit

## Details
fix: panic in WalletSigner::from_private_key (#8052)

* fix: panic in WalletSigner::from_private_key

* stuff

## Patch
### crates/cheatcodes/src/fs.rs
```diff
@@ -376,7 +376,7 @@ fn get_artifact_code(state: &Cheatcodes, path: &str, deployed: bool) -> Result<B
                         let name = file.replace(".sol", "");
                         PathBuf::from(format!("{file}/{name}.json"))
                     }
-                    _ => return Err(fmt_err!("Invalid artifact path")),
+                    _ => bail!("invalid artifact path"),
                 };
 
             state.config.paths.artifacts.join(path_in_artifacts)
```

### crates/cheatcodes/src/script.rs
```diff
@@ -1,7 +1,7 @@
 //! Implementations of [`Scripting`](crate::Group::Scripting) cheatcodes.
 
 use crate::{Cheatcode, CheatsCtxt, DatabaseExt, Result, Vm::*};
-use alloy_primitives::{Address, U256};
+use alloy_primitives::{Address, B256, U256};
 use alloy_signer_wallet::LocalWallet;
 use foundry_wallets::{multi_wallet::MultiWallet, WalletSigner};
 use parking_lot::Mutex;
@@ -106,9 +106,14 @@ impl ScriptWallets {
     }
 
     /// Locks inner Mutex and adds a signer to the [MultiWallet].
-    pub fn add_signer(&self, private_key: impl AsRef<[u8]>) -> Result {
-        self.inner.lock().multi_wallet.add_signer(WalletSigner::from_private_key(private_key)?);
-        Ok(Default::default())
+    pub fn add_private_key(&self, private_key: &B256) -> Result<()> {
+        self.add_local_signer(LocalWallet::from_bytes(private_key)?);
+        Ok(())
+    }
+
+    /// Locks inner Mutex and adds a signer to the [MultiWallet].
+    pub fn add_local_signer(&self, wallet: LocalWallet) {
+        self.inner.lock().multi_wallet.add_signer(WalletSigner::Local(wallet));
     }
 
     /// Locks inner Mutex and returns all signer addresses in the [MultiWallet].
@@ -166,14 +171,13 @@ fn broadcast_key<DB: DatabaseExt>(
     private_key: &U256,
     single_call: bool,
 ) -> Result {
-    let key = super::utils::parse_private_key(private_key)?;
-    let new_origin = LocalWallet::from(key.clone()).address();
+    let wallet = super::utils::parse_wallet(private_key)?;
+    let new_origin = wallet.address();
 
     let result = broadcast(ccx, Some(&new_origin), single_call);
-
     if result.is_ok() {
         if let Some(script_wallets) = &ccx.state.script_wallets {
-            script_wallets.add_signer(key.to_bytes())?;
+            script_wallets.add_local_signer(wallet);
         }
     }
     result
```

### crates/cheatcodes/src/utils.rs
```diff
@@ -90,10 +90,10 @@ impl Cheatcode for deriveKey_3Call {
 impl Cheatcode for rememberKeyCall {
     fn apply_full<DB: DatabaseExt>(&self, ccx: &mut CheatsCtxt<DB>) -> Result {
         let Self { privateKey } = self;
-        let key = parse_private_key(privateKey)?;
-        let address = LocalWallet::from(key.clone()).address();
+        let wallet = parse_wallet(privateKey)?;
+        let address = wallet.address();
         if let Some(script_wallets) = &ccx.state.script_wallets {
-            script_wallets.add_signer(key.to_bytes())?;
+            script_wallets.add_local_signer(wallet);
         }
         Ok(address.abi_encode())
     }
@@ -215,7 +215,7 @@ pub(super) fn sign_with_wallet<DB: DatabaseExt>(
     digest: &B256,
 ) -> Result {
     let Some(script_wallets) = &ccx.state.script_wallets else {
-        return Err("no wallets are available".into());
+        bail!("no wallets are available");
     };
 
     let mut script_wallets = script_wallets.inner.lock();
@@ -229,21 +229,15 @@ pub(super) fn sign_with_wallet<DB: DatabaseExt>(
     } else if signers.len() == 1 {
         *signers.keys().next().unwrap()
     } else {
-        return Err("could not determine signer".into());
+        bail!("could not determine signer");
     };
 
     let wallet = signers
         .get(&signer)
         .ok_or_else(|| fmt_err!("signer with address {signer} is not available"))?;
 
-    let sig =
-        foundry_common::block_on(wallet.sign_hash(digest)).map_err(|err| fmt_err!("{err}"))?;
-
-    debug_assert_eq!(
-        sig.recover_address_from_prehash(digest).map_err(|err| fmt_err!("{err}"))?,
-        signer
-    );
-
+    let sig = foundry_common::block_on(wallet.sign_hash(digest))?;
+    debug_assert_eq!(sig.recover_address_from_prehash(digest)?, signer);
     Ok(encode_vrs(sig))
 }
 
```

### crates/wallets/src/wallet_signer.rs
```diff
@@ -57,9 +57,8 @@ impl WalletSigner {
         }
     }
 
-    pub fn from_private_key(private_key: impl AsRef<[u8]>) -> Result<Self> {
-        let wallet = LocalWallet::from_bytes(&B256::from_slice(private_key.as_ref()))?;
-        Ok(Self::Local(wallet))
+    pub fn from_private_key(private_key: &B256) -> Result<Self> {
+        Ok(Self::Local(LocalWallet::from_bytes(private_key)?))
     }
 
     /// Returns a list of addresses available to use with current signer
@@ -213,7 +212,7 @@ impl PendingSigner {
             }
             Self::Interactive => {
                 let private_key = rpassword::prompt_password("Enter private key:")?;
-                Ok(WalletSigner::from_private_key(hex::decode(private_key)?)?)
+                Ok(WalletSigner::from_private_key(&hex::FromHex::from_hex(private_key)?)?)
             }
         }
     }
```
