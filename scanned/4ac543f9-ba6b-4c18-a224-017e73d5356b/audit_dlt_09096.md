# [?] fix(core/prodtest): Prevent deadlock between secrets-init and tropic-pair.

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-01-16
Source: https://github.com/trezor/trezor-firmware/commit/c9b2230fa8d46db908a6efab7dc236d86e96f152
Type: security-commit

## Details
fix(core/prodtest): Prevent deadlock between secrets-init and tropic-pair.

## Patch
### core/embed/projects/prodtest/.changelog.d/6337.fixed
```diff
@@ -0,0 +1 @@
+Prevent deadlock between secrets-init and tropic-pair.
```

### core/embed/projects/prodtest/cmd/prodtest_tropic.c
```diff
@@ -746,6 +746,29 @@ static void prodtest_tropic_pair(cli_t* cli) {
 
   lt_handle_t* tropic_handle = tropic_get_handle();
 
+  // Retrieve the unprivileged pairing key pair.
+  // NOTE: This ensures that secrets-init has already been called before any
+  // other steps take place. Otherwise, if we wrote Tropic's public key to the
+  // MCU's flash before completing secrets-init, we would run into a deadlock.
+  curve25519_key unprivileged_private = {0};
+  if (secret_key_tropic_pairing_unprivileged(unprivileged_private) != sectrue) {
+    cli_error(cli, CLI_ERROR,
+              "`secret_key_tropic_pairing_unprivileged()` failed.");
+    goto cleanup;
+  }
+  curve25519_key unprivileged_public = {0};
+  curve25519_scalarmult_basepoint(unprivileged_public, unprivileged_private);
+
+  // Retrieve the privileged pairing key pair.
+  curve25519_key privileged_private = {0};
+  if (secret_key_tropic_pairing_privileged(privileged_private) != sectrue) {
+    cli_error(cli, CLI_ERROR,
+              "`secret_key_tropic_pairing_privileged()` failed.");
+    goto cleanup;
+  }
+  curve25519_key privileged_public = {0};
+  curve25519_scalarmult_basepoint(privileged_public, privileged_private);
+
   // Get the Tropic01 public pairing key from the chip's certificate.
   curve25519_key tropic_public = {0};
   if (!tropic_get_pubkey(tropic_public)) {
@@ -777,26 +800,6 @@ static void prodtest_tropic_pair(cli_t* cli) {
     goto cleanup;
   }
 
-  // Retrieve the unprivileged pairing key pair.
-  curve25519_key unprivileged_private = {0};
-  if (secret_key_tropic_pairing_unprivileged(unprivileged_private) != sectrue) {
-    cli_error(cli, CLI_ERROR,
-              "`secret_key_tropic_pairing_unprivileged()` failed.");
-    goto cleanup;
-  }
-  curve25519_key unprivileged_public = {0};
-  curve25519_scalarmult_basepoint(unprivileged_public, unprivileged_private);
-
-  // Retrieve the privileged pairing key pair.
-  curve25519_key privileged_private = {0};
-  if (secret_key_tropic_pairing_privileged(privileged_private) != sectrue) {
-    cli_error(cli, CLI_ERROR,
-              "`secret_key_tropic_pairing_privileged()` failed.");
-    goto cleanup;
-  }
-  curve25519_key privileged_public = {0};
-  curve25519_scalarmult_basepoint(privileged_public, privileged_private);
-
   if (tropic_custom_session_start(TROPIC_FACTORY_PAIRING_KEY_SLOT) == LT_OK) {
     // Write the privileged pairing key to the tropic's pairing key slot if it
     // has not been written yet.
```
