# [?] Fix device crash caused by improper memory alignment of the plugin context buffer

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-12-01
Source: https://github.com/LedgerHQ/app-ethereum/commit/3e750e8419ff2ad1a7eb46d6d7a2a2b88d2d7be4
Type: security-commit

## Details
Fix device crash caused by improper memory alignment of the plugin context buffer

## Patch
### src/shared_context.h
```diff
@@ -65,7 +65,9 @@ typedef struct tokenContext_t {
             uint8_t contractAddress[ADDRESS_LENGTH];
             uint8_t methodSelector[SELECTOR_LENGTH];
         };
-        uint8_t pluginContext[5 * INT256_LENGTH];
+        // This needs to be strictly 4 bytes aligned since pointers to it will be casted as
+        // plugin context struct pointers (structs that contain up to 4 bytes wide elements)
+        uint8_t pluginContext[5 * INT256_LENGTH] __attribute__((aligned(4)));
     };
 
 #ifdef HAVE_STARKWARE
@@ -77,6 +79,8 @@ typedef struct tokenContext_t {
 
 } tokenContext_t;
 
+_Static_assert((offsetof(tokenContext_t, pluginContext) % 4) == 0, "Plugin context not aligned");
+
 typedef struct publicKeyContext_t {
     cx_ecfp_public_key_t publicKey;
     char address[41];
```
