# [?] fix(legacy): Improve handling of value overflows.

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-09-23
Source: https://github.com/trezor/trezor-firmware/commit/ea542943fced278c3563f068c2aa63dda0d1705e
Type: security-commit

## Details
fix(legacy): Improve handling of value overflows.

[no changelog]

## Patch
### crypto/bip32.c
```diff
@@ -204,6 +204,10 @@ int hdnode_private_ckd_bip32(HDNode *inout, uint32_t i) {
   }
 #endif
 
+  if (inout->depth == UINT32_MAX) {
+    return 0;
+  }
+
   if (i & 0x80000000) {  // private derivation
     data[0] = 0;
     memcpy(data + 1, inout->private_key, 32);
@@ -289,6 +293,10 @@ int hdnode_public_ckd(HDNode *inout, uint32_t i) {
     return 0;
   }
 
+  if (inout->depth == UINT32_MAX) {
+    return 0;
+  }
+
   uint8_t data[33 + 4] = {0};
   uint8_t digest[32 + 32] = {0};
   int result = 0;
```

### legacy/firmware/config.c
```diff
@@ -815,7 +815,7 @@ bool config_containsMnemonic(const char *mnemonic) {
 }
 
 /* Check whether pin matches storage.  The pin must be
- * a null-terminated string with at most 9 characters.
+ * a null-terminated string with at most 50 characters.
  */
 bool config_unlock(const char *pin) {
   char oldTiny = usbTiny(1);
```

### legacy/firmware/fsm_msg_nem.h
```diff
@@ -164,7 +164,12 @@ void fsm_msgNEMSignTx(NEMSignTx *msg) {
   hdnode_get_nem_address(node, common->network, address);
 
   if (msg->has_transfer) {
-    nem_canonicalizeMosaics(&msg->transfer);
+    if (!nem_canonicalizeMosaics(&msg->transfer)) {
+      fsm_sendFailure(FailureType_Failure_ProcessError,
+                      _("Failed to canonicalize mosaics"));
+      layoutHome();
+      return;
+    }
   }
 
   if (msg->has_transfer && !nem_askTransfer(common, &msg->transfer, network)) {
```

### legacy/firmware/layout2.c
```diff
@@ -581,11 +581,18 @@ static bool formatComputedFeeRate(uint64_t fee, uint64_t tx_weight,
   // Compute fee rate and modify it in place for the bn_format_amount()
   // function. We multiply by 100, because we want bn_format_amount() to display
   // two decimal digits.
-  uint64_t fee_rate_multiplied = div_round(100 * fee, tx_size);
-
-  size_t length =
-      bn_format_amount(fee_rate_multiplied, parentheses ? "(" : NULL,
-                       segwit ? " sat/vB" : " sat/B", 2, output, output_length);
+  int decimals = 2;
+  int multiplier = 100;
+  if (fee > (UINT64_MAX / multiplier)) {
+    // Value overflow. Omit the decimal digits.
+    decimals = 0;
+    multiplier = 1;
+  }
+  uint64_t fee_rate_multiplied = div_round(multiplier * fee, tx_size);
+
+  size_t length = bn_format_amount(
+      fee_rate_multiplied, parentheses ? "(" : NULL,
+      segwit ? " sat/vB" : " sat/B", decimals, output, output_length);
   if (length == 0) {
     return false;
   }
```

### legacy/firmware/nem2.c
```diff
@@ -651,11 +651,11 @@ static inline size_t format_amount(const NEMMosaicDefinition *definition,
       -divisor, false, ',', str_out, size);
 }
 
-void nem_canonicalizeMosaics(NEMTransfer *transfer) {
+bool nem_canonicalizeMosaics(NEMTransfer *transfer) {
   size_t old_count = transfer->mosaics_count;
 
   if (old_count <= 1) {
-    return;
+    return true;
   }
 
   NEMMosaic *const mosaics = transfer->mosaics;
@@ -682,6 +682,10 @@ void nem_canonicalizeMosaics(NEMTransfer *transfer) {
 
       if (nem_mosaicCompare(mosaic, new_mosaic) == 0) {
         skip[j] = true;
+        if (mosaic->quantity + new_mosaic->quantity < mosaic->quantity) {
+          // quantity overflow
+          return false;
+        }
         mosaic->quantity += new_mosaic->quantity;
       }
     }
@@ -704,6 +708,7 @@ void nem_canonicalizeMosaics(NEMTransfer *transfer) {
       }
     }
   }
+  return true;
 }
 
 void nem_mosaicFormatAmount(const NEMMosaicDefinition *definition,
```

### legacy/firmware/nem2.h
```diff
@@ -92,7 +92,7 @@ const NEMMosaicDefinition *nem_mosaicByName(const char *namespace,
                                             const char *mosaic,
                                             uint8_t network);
 
-void nem_canonicalizeMosaics(NEMTransfer *transfer);
+bool nem_canonicalizeMosaics(NEMTransfer *transfer);
 void nem_mosaicFormatAmount(const NEMMosaicDefinition *definition,
                             uint64_t quantity, const bignum256 *multiplier,
                             char *str_out, size_t size);
```

### tests/device_tests/bitcoin/test_signtx.py
```diff
@@ -732,6 +732,47 @@ def test_fee_high_hardfail(session: Session):
     )
 
 
+@pytest.mark.models("legacy")
+def test_fee_rate_overflow(session: Session):
+    # Adds a UI fixture for a transaction that used to cause a fee rate overflow on T1.
+    inp1 = messages.TxInputType(
+        # tb1pn2d0yjeedavnkd8z8lhm566p0f2utm3lgvxrsdehnl94y34txmts5s7t4c
+        address_n=parse_path("m/86h/1h/0h/1/0"),
+        amount=185_000_000_000_000_000,
+        prev_hash=TXHASH_ec5194,
+        prev_index=0,
+        script_type=messages.InputScriptType.SPENDTAPROOT,
+    )
+    out1 = messages.TxOutputType(
+        # 86'/1'/1'/0/0
+        address="tb1paxhjl357yzctuf3fe58fcdx6nul026hhh6kyldpfsf3tckj9a3wslqd7zd",
+        amount=100_000_000,
+        script_type=messages.OutputScriptType.PAYTOADDRESS,
+    )
+    with session.client as client:
+        client.set_expected_responses(
+            [
+                request_input(0),
+                request_output(0),
+                messages.ButtonRequest(code=B.ConfirmOutput),
+                (is_core(session), messages.ButtonRequest(code=B.ConfirmOutput)),
+                messages.ButtonRequest(code=B.FeeOverThreshold),
+                messages.ButtonRequest(code=B.SignTx),
+                request_input(0),
+                request_output(0),
+                request_input(0),
+                request_finished(),
+            ]
+        )
+        btc.sign_tx(
+            session,
+            "Testnet",
+            [inp1],
+            [out1],
+            prev_txes=TX_CACHE_TESTNET,
+        )
+
+
 def test_not_enough_funds(session: Session):
     # input tx: d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882
 
```

### tests/ui_tests/fixtures.json
```diff
@@ -270,6 +270,7 @@
 "T1B1_en_bitcoin-test_signtx.py::test_attack_modify_change_address": "5a309a1de343c16239ab822e0434afe0cee621c09c6b4aa882ca7bbd81f4c4a4",
 "T1B1_en_bitcoin-test_signtx.py::test_change_on_main_chain_allowed": "5a309a1de343c16239ab822e0434afe0cee621c09c6b4aa882ca7bbd81f4c4a4",
 "T1B1_en_bitcoin-test_signtx.py::test_fee_high_warning": "2521cfd56ed52e4705470aadd4760082d2cd145cabb9cb4abb53c611818148be",
+"T1B1_en_bitcoin-test_signtx.py::test_fee_rate_overflow": "68444d8d472ad9b0a8428bfc01d9f5f3093e106c00d4ae6b980642671457dd17",
 "T1B1_en_bitcoin-test_signtx.py::test_incorrect_input_script_type[InputScriptType.EXTERNAL]": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
 "T1B1_en_bitcoin-test_signtx.py::test_incorrect_input_script_type[InputScriptType.SPENDADDRESS]": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
 "T1B1_en_bitcoin-test_signtx.py::test_incorrect_output_script_type[OutputScriptType.PAYTOADDRESS]": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
```
