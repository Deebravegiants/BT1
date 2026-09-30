# [?] Fix crash when mining with empty keypool.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2015-08-18
Source: https://github.com/zcash/zcash/commit/95d1f887ca66feb1d573affc761d1fa957ac88e9
Type: security-commit

## Details
Fix crash when mining with empty keypool.

Since the introduction of the ScriptForMining callback, the mining
functions (setgenerate and generate) crash with an assertion failure
(due to a NULL pointer script returned) if the keypool is empty.  Fix
this by giving a proper error.

Zcash: Adapted to our MinerAddress type.

Co-authored-by: Jack Grigg <jack@electriccoin.co>

## Patch
### qa/rpc-tests/keypool.py
```diff
@@ -8,7 +8,7 @@
 # Add python-bitcoinrpc to module search path:
 
 from test_framework.authproxy import JSONRPCException
-from test_framework.util import check_json_precision, initialize_chain, \
+from test_framework.util import assert_equal, check_json_precision, initialize_chain, \
     start_nodes, start_node, stop_nodes, wait_bitcoinds, bitcoind_processes
 
 import os
@@ -72,6 +72,21 @@ def run_test(nodes, tmpdir):
     except JSONRPCException as e:
         assert(e.error['code']==-12)
 
+    # refill keypool with three new addresses
+    nodes[0].walletpassphrase('test', 12000)
+    nodes[0].keypoolrefill(3)
+    nodes[0].walletlock()
+
+    # drain them by mining
+    nodes[0].generate(1)
+    nodes[0].generate(1)
+    nodes[0].generate(1)
+    nodes[0].generate(1)
+    try:
+        nodes[0].generate(1)
+        raise AssertionError('Keypool should be exhausted after three addesses')
+    except JSONRPCException as e:
+        assert_equal(e.error['code'], -12)
 
 def main():
     import optparse
```

### src/miner.cpp
```diff
@@ -116,10 +116,6 @@ void UpdateTime(CBlockHeader* pblock, const Consensus::Params& consensusParams,
     }
 }
 
-bool IsValidMinerAddress(const MinerAddress& minerAddr) {
-    return minerAddr.which() != 0;
-}
-
 class AddFundingStreamValueToTx : public boost::static_visitor<bool>
 {
 private:
@@ -742,7 +738,7 @@ void static BitcoinMiner(const CChainParams& chainparams)
 
     try {
         // Throw an error if no address valid for mining was provided.
-        if (!IsValidMinerAddress(minerAddress)) {
+        if (!boost::apply_visitor(IsValidMinerAddress(), minerAddress)) {
             throw std::runtime_error("No miner address available (mining requires a wallet or -mineraddress)");
         }
 
```

### src/miner.h
```diff
@@ -41,7 +41,24 @@ class KeepMinerAddress : public boost::static_visitor<>
     }
 };
 
-bool IsValidMinerAddress(const MinerAddress& minerAddr);
+class IsValidMinerAddress : public boost::static_visitor<bool>
+{
+public:
+    IsValidMinerAddress() {}
+
+    bool operator()(const InvalidMinerAddress &invalid) const {
+        return false;
+    }
+    bool operator()(const libzcash::SaplingPaymentAddress &pa) const {
+        return true;
+    }
+    bool operator()(const boost::shared_ptr<CReserveScript> &coinbaseScript) const {
+        // Return false if no script was provided.  This can happen
+        // due to some internal error but also if the keypool is empty.
+        // In the latter case, already the pointer is NULL.
+        return coinbaseScript.get() && !coinbaseScript->reserveScript.empty();
+    }
+};
 
 struct CBlockTemplate
 {
```

### src/rpc/mining.cpp
```diff
@@ -188,8 +188,14 @@ UniValue generate(const UniValue& params, bool fHelp)
     MinerAddress minerAddress;
     GetMainSignals().AddressForMining(minerAddress);
 
+    // If the keypool is exhausted, no script is returned at all.  Catch this.
+    auto resv = boost::get<boost::shared_ptr<CReserveScript>>(&minerAddress);
+    if (resv && !resv->get()) {
+        throw JSONRPCError(RPC_WALLET_KEYPOOL_RAN_OUT, "Error: Keypool ran out, please call keypoolrefill first");
+    }
+
     // Throw an error if no address valid for mining was provided.
-    if (!IsValidMinerAddress(minerAddress)) {
+    if (!boost::apply_visitor(IsValidMinerAddress(), minerAddress)) {
         throw JSONRPCError(RPC_INTERNAL_ERROR, "No miner address available (mining requires a wallet or -mineraddress)");
     }
 
@@ -622,7 +628,7 @@ UniValue getblocktemplate(const UniValue& params, bool fHelp)
         GetMainSignals().AddressForMining(minerAddress);
 
         // Throw an error if no address valid for mining was provided.
-        if (!IsValidMinerAddress(minerAddress)) {
+        if (!boost::apply_visitor(IsValidMinerAddress(), minerAddress)) {
             throw JSONRPCError(RPC_INTERNAL_ERROR, "No miner address available (mining requires a wallet or -mineraddress)");
         }
 
```

### src/wallet/wallet.cpp
```diff
@@ -4418,8 +4418,12 @@ void CWallet::GetAddressForMining(MinerAddress &minerAddress)
 
     boost::shared_ptr<CReserveKey> rKey(new CReserveKey(this));
     CPubKey pubkey;
-    if (!rKey->GetReservedKey(pubkey))
+    if (!rKey->GetReservedKey(pubkey)) {
+        // Explicitly return nullptr to indicate that the keypool is empty.
+        rKey = nullptr;
+        minerAddress = rKey;
         return;
+    }
 
     rKey->reserveScript = CScript() << OP_DUP << OP_HASH160 << ToByteVector(pubkey.GetID()) << OP_EQUALVERIFY << OP_CHECKSIG;
     minerAddress = rKey;
```
