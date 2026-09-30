# [?] Fix Ursa crypto provider crashes on errors

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2019-09-11
Source: https://github.com/hyperledger-iroha/iroha/commit/4af3143bbb77506ce2a6533346b75f27edb21c72
Type: security-commit

## Details
Fix Ursa crypto provider crashes on errors

Signed-off-by: Andrei Lebedev <lebdron@gmail.com>

## Patch
### shared_model/cryptography/ed25519_ursa_impl/crypto_provider.cpp
```diff
@@ -25,7 +25,8 @@ namespace shared_model {
       if (!ursa_ed25519_sign(&kMessage, &kPrivateKey, &signature, &err)) {
         // handle error
         ursa_ed25519_string_free(err.message);
-      };
+        return Signed{""};
+      }
 
       Signed result(std::string((const std::string::value_type *)signature.data,
                                 signature.len));
@@ -67,7 +68,8 @@ namespace shared_model {
       if (!ursa_ed25519_keypair_new(&public_key, &private_key, &err)) {
         // handle error
         ursa_ed25519_string_free(err.message);
-      };
+        return Keypair{PublicKey{""}, PrivateKey{""}};
+      }
 
       Keypair result(PublicKey(std::string(
                          (const std::string::value_type *)public_key.data,
@@ -94,7 +96,8 @@ namespace shared_model {
               &kSeed, &public_key, &private_key, &err)) {
         // handle error
         ursa_ed25519_string_free(err.message);
-      };
+        return Keypair{PublicKey{""}, PrivateKey{""}};
+      }
 
       Keypair result(PublicKey(std::string(
                          (const std::string::value_type *)public_key.data,
```
