# [?] Merge branch 'aleks/wallet-fix-empty-password-panic' (#2473)

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-01-31
Source: https://github.com/namada-net/namada/commit/794f6a2bdeb00511abeb6636344cc0fc894a1a6c
Type: security-commit

## Details
Merge branch 'aleks/wallet-fix-empty-password-panic' (#2473)

* origin/aleks/wallet-fix-empty-password-panic:
  Add changelog
  Unify list/find commands output
  Check if provided password is empty

## Patch
### .changelog/unreleased/bug-fixes/2473-wallet-fix-empty-password-panic.md
```diff
@@ -0,0 +1,2 @@
+- Wallet: handle the case when empty decryption password is provided.
+  ([\#2473](https://github.com/anoma/namada/pull/2473))
```

### crates/apps/src/lib/cli/wallet.rs
```diff
@@ -110,33 +110,42 @@ fn shielded_keys_list(
             display_line!(io, &mut w_lock; "    Viewing Key: {}", key).unwrap();
             // A subset of viewing keys will have corresponding spending keys.
             // Print those too if they are available and requested.
-            if unsafe_show_secret {
-                if let Some(spending_key) = spending_key_opt {
-                    match spending_key.get::<CliWalletUtils>(decrypt, None) {
-                        // Here the spending key is unencrypted or successfully
-                        // decrypted
-                        Ok(spending_key) => {
+            if let Some(spending_key) = spending_key_opt {
+                match spending_key.get::<CliWalletUtils>(decrypt, None) {
+                    // Here the spending key is unencrypted or successfully
+                    // decrypted
+                    Ok(spending_key) => {
+                        if unsafe_show_secret {
                             display_line!(io,
                                 &mut w_lock;
                                 "    Spending key: {}", spending_key,
                             )
                             .unwrap();
                         }
-                        // Here the key is encrypted but decryption has not been
-                        // requested
-                        Err(DecryptionError::NotDecrypting) if !decrypt => {
-                            continue;
-                        }
-                        // Here the key is encrypted but incorrect password has
-                        // been provided
-                        Err(err) => {
-                            display_line!(io,
-                                &mut w_lock;
-                                    "    Couldn't decrypt the spending key: {}",
-                                    err,
-                            )
-                            .unwrap();
-                        }
+                    }
+                    // Here the key is encrypted but decryption has not been
+                    // requested
+                    Err(DecryptionError::NotDecrypting) if !decrypt => {
+                        continue;
+                    }
+                    // Here the key is encrypted but no password has been
+                    // provided
+                    Err(DecryptionError::EmptyPassword) => {
+                        display_line!(io,
+                                      &mut w_lock;
+                                      "Decryption of the spending key cancelled: no password provided"
+                        )
+                        .unwrap();
+                    }
+                    // Here the key is encrypted but incorrect password has
+                    // been provided
+                    Err(err) => {
+                        display_line!(io,
+                            &mut w_lock;
+                                "    Couldn't decrypt the spending key: {}",
+                                err,
+                        )
+                        .unwrap();
                     }
                 }
             }
@@ -1018,10 +1027,18 @@ fn transparent_key_address_find_by_alias(
                 match wallet.find_secret_key(&alias, None) {
                     Ok(keypair) => {
                         if unsafe_show_secret {
-                            display_line!(io, &mut w_lock; "    Secret key: {}", keypair)
-                        .unwrap();
+                            display_line!(io, &mut w_lock; "    Secret key: {}", keypair) .unwrap();
                         }
                     }
+                    Err(FindKeyError::KeyDecryptionError(
+                        DecryptionError::EmptyPassword,
+                    )) => {
+                        display_line!(io,
+                                      &mut w_lock;
+                                      "Decryption of the keypair cancelled: no password provided"
+                        )
+                        .unwrap();
+                    }
                     Err(FindKeyError::KeyNotFound(_)) => {}
                     Err(err) => edisplay_line!(io, "{}", err),
                 }
@@ -1088,6 +1105,15 @@ fn shielded_key_address_find_by_alias(
                             display_line!(io, &mut w_lock; "    Spending key: {}", spending_key).unwrap();
                         }
                     }
+                    Err(FindKeyError::KeyDecryptionError(
+                        DecryptionError::EmptyPassword,
+                    )) => {
+                        display_line!(io,
+                                      &mut w_lock;
+                                      "Decryption of the shielded key cancelled: no password provided"
+                        )
+                        .unwrap();
+                    }
                     Err(FindKeyError::KeyNotFound(_)) => {}
                     Err(err) => edisplay_line!(io, "{}", err),
                 }
@@ -1157,14 +1183,22 @@ fn transparent_keys_list(
             // Print those too if they are available and requested.
             if let Some((stored_keypair, _pkh)) = stored_keypair {
                 match stored_keypair.get::<CliWalletUtils>(decrypt, None) {
-                    Ok(keypair) if unsafe_show_secret => {
+                    Ok(keypair) => {
+                        if unsafe_show_secret {
+                            display_line!(io,
+                                          &mut w_lock;
+                                          "    Secret key: {}", keypair,
+                            )
+                            .unwrap();
+                        }
+                    }
+                    Err(DecryptionError::EmptyPassword) => {
                         display_line!(io,
                                       &mut w_lock;
-                                      "    Secret key: {}", keypair,
+                                      "Decryption of the keypair cancelled: no password provided"
                         )
                         .unwrap();
                     }
-                    Ok(_keypair) => {}
                     Err(DecryptionError::NotDecrypting) if !decrypt => {
                         continue;
                     }
```

### crates/sdk/src/wallet/keys.rs
```diff
@@ -144,6 +144,8 @@ pub enum DecryptionError {
     DeserializingError,
     #[error("Asked not to decrypt")]
     NotDecrypting,
+    #[error("Empty password provided")]
+    EmptyPassword,
 }
 
 impl<T: BorshSerialize + BorshDeserialize + Display + FromStr + Clone>
@@ -217,6 +219,10 @@ impl<T: BorshSerialize + BorshDeserialize> EncryptedKeypair<T> {
         &self,
         password: Zeroizing<String>,
     ) -> Result<T, DecryptionError> {
+        if password.is_empty() {
+            return Err(DecryptionError::EmptyPassword);
+        }
+
         let salt_len = encryption_salt().len();
         let (raw_salt, cipher) = self.0.split_at(salt_len);
 
```
