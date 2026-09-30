# [?] [backport] fix assert crash when specified change output spend size is unknown

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2022-10-27
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/47a6e9cfed2575baf4852b9af1832ba698a0b5fb
Type: security-commit

## Details
[backport] fix assert crash when specified change output spend size is unknown

## Patch
### src/wallet/test/wallet_tests.cpp
```diff
@@ -9,8 +9,11 @@
 #include <consensus/validation.h>
 #include <interfaces/chain.h>
 #include <key.h>
+#include <keystore.h>
+#include <policy/policy.h>
 #include <pubkey.h>
 #include <rpc/server.h>
+#include <script/sign.h>
 #include <util/defer.h>
 #include <validation.h>
 #include <wallet/coincontrol.h>
@@ -560,6 +563,43 @@ BOOST_FIXTURE_TEST_CASE(wallet_disableprivkeys, TestChain100Setup) {
     BOOST_CHECK(!wallet->GetKeyFromPool(pubkey, false));
 }
 
+// Explicit calculation which is used to test the wallet constant
+static size_t CalculateP2PKHInputSize(bool use_max_sig) {
+    // Generate ephemeral valid pubkey
+    CKey key;
+    key.MakeNewKey(true);
+    CPubKey pubkey = key.GetPubKey();
+
+    // Generate pubkey hash
+    CKeyID key_hash = pubkey.GetID();
+
+    // Create script to enter into keystore. Key hash can't be 0...
+    CScript script = GetScriptForDestination(key_hash);
+
+    // Add script to key store and key to watchonly
+    CBasicKeyStore keystore;
+    keystore.AddKeyPubKey(key, pubkey);
+
+    // Fill in dummy signatures for fee calculation.
+    SignatureData sig_data;
+    if (!ProduceSignature(keystore,
+                          use_max_sig ? DUMMY_MAXIMUM_SIGNATURE_CREATOR
+                                      : DUMMY_SIGNATURE_CREATOR,
+                          script, sig_data, std::nullopt)) {
+        // We're hand-feeding it correct arguments; shouldn't happen
+        assert(false);
+    }
+
+    CTxIn tx_in;
+    UpdateInput(tx_in, sig_data);
+    return static_cast<size_t>(GetVirtualTransactionInputSize(tx_in, 1, nBytesPerSigCheck));
+}
+
+BOOST_FIXTURE_TEST_CASE(dummy_input_size_test, TestChain100Setup) {
+    BOOST_CHECK(CalculateP2PKHInputSize(false) <= DUMMY_P2PKH_INPUT_SIZE);
+    BOOST_CHECK_EQUAL(CalculateP2PKHInputSize(true), DUMMY_P2PKH_INPUT_SIZE);
+}
+
 BOOST_FIXTURE_TEST_CASE(wallet_bip69, ListCoinsTestingSetup) {
     Defer d([]{
         // undo forceSetArg
```

### src/wallet/wallet.cpp
```diff
@@ -1699,8 +1699,6 @@ int64_t CalculateMaximumSignedTxSize(const CTransaction &tx,
                                      bool use_max_sig) {
     CMutableTransaction txNew(tx);
     if (!wallet->DummySignTx(txNew, txouts, use_max_sig)) {
-        // This should never happen, because IsAllFromMe(ISMINE_SPENDABLE)
-        // implies that we can sign for every input.
         return -1;
     }
     return GetSerializeSize(txNew, PROTOCOL_VERSION);
@@ -1711,8 +1709,6 @@ int CalculateMaximumSignedInputSize(const CTxOut &txout, const CWallet *wallet,
     CMutableTransaction txn;
     txn.vin.push_back(CTxIn(COutPoint()));
     if (!wallet->DummySignInput(txn.vin[0], txout, use_max_sig)) {
-        // This should never happen, because IsAllFromMe(ISMINE_SPENDABLE)
-        // implies that we can sign for every input.
         return -1;
     }
     return GetSerializeSize(txn.vin[0], PROTOCOL_VERSION);
@@ -3209,9 +3205,14 @@ CreateTransactionResult CWallet::CreateTransaction(
             if (pick_new_inputs) {
                 nValueIn = Amount::zero();
                 setCoins.clear();
-                coin_selection_params.change_spend_size =
-                    CalculateMaximumSignedInputSize(change_prototype_txout,
-                                                    this);
+                const int change_spend_size = CalculateMaximumSignedInputSize(change_prototype_txout, this);
+                // If the wallet doesn't know how to sign change output, assume
+                // p2pkh as lower-bound to allow BnB to do it's thing
+                if (change_spend_size == -1) {
+                    coin_selection_params.change_spend_size = DUMMY_P2PKH_INPUT_SIZE;
+                } else {
+                    coin_selection_params.change_spend_size = static_cast<size_t>(change_spend_size);
+                }
                 coin_selection_params.effective_fee = nFeeRateNeeded;
                 if (!SelectCoins(vAvailableCoins, nValueToSelect, setCoins,
                                  nValueIn, coinControl, coin_selection_params,
```

### src/wallet/wallet.h
```diff
@@ -95,6 +95,8 @@ static constexpr bool DEFAULT_USE_BIP69 = true;
 static constexpr bool DEFAULT_ALLOW_LEGACY_P2SH = false;
 //! Default for the RPC option "include_unsafe"
 static constexpr bool DEFAULT_INCLUDE_UNSAFE_INPUTS = false;
+//! Pre-calculated constant for input size estimation
+static constexpr size_t DUMMY_P2PKH_INPUT_SIZE = 148;
 
 class CChainParams;
 class CCoinControl;
```

### test/functional/rpc_psbt.py
```diff
@@ -139,8 +139,18 @@ def run_test(self):
         self.generate(self.nodes[0], 6)
         self.sync_all()
 
+        block_height = self.nodes[0].getblockcount()
         unspent = self.nodes[0].listunspent()[0]
 
+        # Make sure change address wallet does not have P2SH innerscript access to results in success
+        # when attempting BnB coin selection
+        self.nodes[0].walletcreatefundedpsbt(
+            [],
+            [{self.nodes[2].getnewaddress():unspent["amount"] + 1}],
+            block_height + 2,
+            {"changeAddress": self.nodes[1].getnewaddress()},
+            False)
+
         # Regression test for 14473 (mishandling of already-signed
         # transaction):
         psbtx_info = self.nodes[0].walletcreatefundedpsbt([{"txid": unspent["txid"], "vout":unspent["vout"]}], [
```
