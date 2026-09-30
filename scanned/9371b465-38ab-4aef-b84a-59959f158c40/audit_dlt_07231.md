# [?] [chore] Remove RUSTSEC-2024-0421 (#21317)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-02-22
Source: https://github.com/MystenLabs/sui/commit/3779afd2a451325fd87c9353a2c1817aa7c5a17a
Type: security-commit

## Details
[chore] Remove RUSTSEC-2024-0421 (#21317)

## Description 

Updates `passkey` crates to `v0.4.0` which uses `idna v1.0.3`. Any
`idna` with a version >=1.0.0 is good for this RUSTSEC-2024-0421.

Note: updated the passkey's `UserValidationMethod` trait impl for
`MyUserValidationMethod` by following the changes to the example here:

https://github.com/1Password/passkey-rs/pull/24/files#diff-b96910ff4357fe0cced6689937c8ff57c8b232150b132c781fc8098de95fce7cR12-R26

## Test plan 

How did you test the new or updated feature?

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

## Patch
### Cargo.lock
```diff
@@ -6103,16 +6103,6 @@ version = "1.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b9e0384b61958566e926dc50660321d12159025e767c18e043daf26b70104c39"
 
-[[package]]
-name = "idna"
-version = "0.5.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "634d9b1461af396cad843f47fdba5597a4f9e6ddd4bfb6ff5d85028c25cb12f6"
-dependencies = [
- "unicode-bidi",
- "unicode-normalization",
-]
-
 [[package]]
 name = "idna"
 version = "1.0.3"
@@ -9407,9 +9397,9 @@ dependencies = [
 
 [[package]]
 name = "passkey-authenticator"
-version = "0.2.0"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4017d27e98940a98358b43a3fe19cb3d7b7c821c3b35634d8087230e92445579"
+checksum = "f9b065ce31354bcf23a333003c77f0d71f00eb95761b3390a069546e078a7a5b"
 dependencies = [
  "async-trait",
  "coset",
@@ -9421,13 +9411,13 @@ dependencies = [
 
 [[package]]
 name = "passkey-client"
-version = "0.2.0"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f14d42b14749cc7927add34a9932b3b3cc5349a633384850baa67183061439dd"
+checksum = "5080bfafe23d139ae8be8b907453aee0b8af3ca7cf25d1f8d7bfcf7b079d3412"
 dependencies = [
  "ciborium",
  "coset",
- "idna 0.5.0",
+ "idna",
  "passkey-authenticator",
  "passkey-types",
  "public-suffix",
@@ -9439,21 +9429,24 @@ dependencies = [
 
 [[package]]
 name = "passkey-types"
-version = "0.2.0"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "499cff8432e71c5f8784d9645aac0f9fca604d67f59b68a606170b5e229c6538"
+checksum = "77144664f6aac5f629d7efa815f5098a054beeeca6ccafee5ec453fd2b0c53f9"
 dependencies = [
  "bitflags 2.6.0",
  "ciborium",
  "coset",
  "data-encoding",
+ "getrandom 0.2.15",
+ "hmac",
  "indexmap 2.7.0",
  "rand 0.8.5",
  "serde",
  "serde_json",
  "sha2 0.10.8",
  "strum 0.25.0",
  "typeshare",
+ "zeroize",
 ]
 
 [[package]]
@@ -17736,7 +17729,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "32f8b686cadd1473f4bd0117a5d28d36b1ade384ea9b5069a1c40aefed7fda60"
 dependencies = [
  "form_urlencoded",
- "idna 1.0.3",
+ "idna",
  "percent-encoding",
  "serde",
 ]
```

### Cargo.toml
```diff
@@ -592,9 +592,9 @@ fastcrypto-zkp = { git = "https://github.com/MystenLabs/fastcrypto", rev = "69d4
 fastcrypto-vdf = { git = "https://github.com/MystenLabs/fastcrypto", rev = "69d496c71fb37e3d22fe85e5bbfd4256d61422b9", features = [
     "experimental",
 ] }
-passkey-types = { version = "0.2.0" }
-passkey-client = { version = "0.2.0" }
-passkey-authenticator = { version = "0.2.0" }
+passkey-types = { version = "0.4.0" }
+passkey-client = { version = "0.4.0" }
+passkey-authenticator = { version = "0.4.0" }
 coset = "0.3"
 p256 = { version = "0.13.2", features = ["ecdsa"] }
 
```

### crates/sui-e2e-tests/tests/passkey_e2e_tests.rs
```diff
@@ -2,10 +2,10 @@
 // SPDX-License-Identifier: Apache-2.0
 use fastcrypto::traits::ToFromBytes;
 use p256::pkcs8::DecodePublicKey;
-use passkey_authenticator::{Authenticator, UserValidationMethod};
+use passkey_authenticator::{Authenticator, UserCheck, UserValidationMethod};
 use passkey_client::Client;
 use passkey_types::{
-    ctap2::Aaguid,
+    ctap2::{Aaguid, Ctap2Error},
     rand::random_vec,
     webauthn::{
         AttestationConveyancePreference, CredentialCreationOptions, CredentialRequestOptions,
@@ -38,12 +38,18 @@ use url::Url;
 struct MyUserValidationMethod {}
 #[async_trait::async_trait]
 impl UserValidationMethod for MyUserValidationMethod {
-    async fn check_user_presence(&self) -> bool {
-        true
-    }
+    type PasskeyItem = Passkey;
 
-    async fn check_user_verification(&self) -> bool {
-        true
+    async fn check_user<'a>(
+        &self,
+        _credential: Option<&'a Passkey>,
+        presence: bool,
+        verification: bool,
+    ) -> Result<UserCheck, Ctap2Error> {
+        Ok(UserCheck {
+            presence,
+            verification,
+        })
     }
 
     fn is_verification_enabled(&self) -> Option<bool> {
```

### crates/sui-types/src/unit_tests/passkey_authenticator_test.rs
```diff
@@ -19,10 +19,10 @@ use fastcrypto::hash::HashFunction;
 use fastcrypto::rsa::{Base64UrlUnpadded, Encoding as _};
 use fastcrypto::traits::ToFromBytes;
 use p256::pkcs8::DecodePublicKey;
-use passkey_authenticator::{Authenticator, UserValidationMethod};
+use passkey_authenticator::{Authenticator, UserCheck, UserValidationMethod};
 use passkey_client::Client;
 use passkey_types::{
-    ctap2::Aaguid,
+    ctap2::{Aaguid, Ctap2Error},
     rand::random_vec,
     webauthn::{
         AttestationConveyancePreference, CredentialCreationOptions, CredentialRequestOptions,
@@ -39,12 +39,18 @@ use url::Url;
 pub struct MyUserValidationMethod {}
 #[async_trait::async_trait]
 impl UserValidationMethod for MyUserValidationMethod {
-    async fn check_user_presence(&self) -> bool {
-        true
-    }
-
-    async fn check_user_verification(&self) -> bool {
-        true
+    type PasskeyItem = Passkey;
+
+    async fn check_user<'a>(
+        &self,
+        _credential: Option<&'a Passkey>,
+        presence: bool,
+        verification: bool,
+    ) -> Result<UserCheck, Ctap2Error> {
+        Ok(UserCheck {
+            presence,
+            verification,
+        })
     }
 
     fn is_verification_enabled(&self) -> Option<bool> {
```

### deny.toml
```diff
@@ -34,8 +34,6 @@ ignore = [
     "RUSTSEC-2024-0384",
     # allow unmaintained derivative crate used in transitive dependencies (ark-*)
     "RUSTSEC-2024-0388",
-    # allow outdated 'idna' until passkey-client crate is able to update
-    "RUSTSEC-2024-0421",
     # allow unmaintained ring
     "RUSTSEC-2025-0007"
 ]
```
