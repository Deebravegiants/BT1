# [?] Fix Swap crash

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2025-07-01
Source: https://github.com/LedgerHQ/app-ethereum/commit/52925a19fbedbd27bca60bf6de4ae8314a337ee7
Type: security-commit

## Details
Fix Swap crash

## Patch
### src/handle_swap_sign_transaction.c
```diff
@@ -153,18 +153,13 @@ void __attribute__((noreturn)) swap_finalize_exchange_sign_transaction(bool is_s
 
 void __attribute__((noreturn)) handle_swap_sign_transaction(const chain_config_t* config) {
     chainConfig = config;
-    reset_app_context();
     G_called_from_swap = true;
     G_swap_response_ready = false;
     // If we are in crosschain context, automatically register the CROSSCHAIN plugin
     if (G_swap_mode == SWAP_MODE_CROSSCHAIN_PENDING_CHECK) {
         set_swap_with_calldata_plugin_type();
     }
 
-    common_app_init();
-
-    storage_init();
-
 #ifdef SCREEN_SIZE_WALLET
     nbgl_useCaseSpinner("Signing");
 #endif  // SCREEN_SIZE_WALLET
```

### src/main.c
```diff
@@ -357,7 +357,7 @@ static void init_coin_config(chain_config_t *coin_config) {
     coin_config->chainId = APP_CHAIN_ID;
 }
 
-void storage_init(void) {
+static void storage_init(void) {
     internalStorage_t storage;
     if (N_storage.initialized) {
         return;
@@ -368,6 +368,22 @@ void storage_init(void) {
     nvm_write((void *) &N_storage, (void *) &storage, sizeof(internalStorage_t));
 }
 
+// Common initialization for the application, both in Standalone or Library mode (Swap)
+static void app_init(bool library_mode) {
+    reset_app_context();
+    common_app_init();
+    storage_init();
+    if (library_mode == false) {
+        app_mem_init();
+        // If we are not in library mode, we need to initialize the UX
+        io_init();
+        ui_idle();
+    }
+
+    // to prevent it from having a fixed value at boot
+    roll_challenge();
+}
+
 void coin_main(eth_libargs_t *args) {
     chain_config_t config;
     if (args) {
@@ -387,16 +403,7 @@ void coin_main(eth_libargs_t *args) {
         chainConfig = &config;
     }
 
-    reset_app_context();
-    storage_init();
-    common_app_init();
-
-    io_init();
-    app_mem_init();
-    ui_idle();
-
-    // to prevent it from having a fixed value at boot
-    roll_challenge();
+    app_init(false);
 
     app_main();
 }
@@ -419,12 +426,12 @@ __attribute__((noreturn)) void library_main(eth_libargs_t *args) {
             break;
         case SIGN_TRANSACTION:
             if (copy_transaction_parameters(args->create_transaction, args->chain_config)) {
+                app_init(true);
                 // never returns
                 handle_swap_sign_transaction(args->chain_config);
-            } else {
-                // Failed to copy, non recoverable
-                app_quit();
             }
+            // Failed to copy, non recoverable
+            app_quit();
             break;
         case GET_PRINTABLE_AMOUNT:
             if (handle_get_printable_amount(args->get_printable_amount, args->chain_config) !=
```

### src/shared_context.h
```diff
@@ -188,4 +188,3 @@ extern uint32_t eth2WithdrawalIndex;
 void app_quit(void);
 void reset_app_context(void);
 const uint8_t *parseBip32(const uint8_t *dataBuffer, uint8_t *dataLength, bip32_path_t *bip32);
-void storage_init(void);
```
