# [?] Add -orchardactionlimit parameter to guard against memory exhaustion.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2022-05-02
Source: https://github.com/zcash/zcash/commit/a71db41d38d9dcedc16eec2818c03e9234a9ed9a
Type: security-commit

## Details
Add -orchardactionlimit parameter to guard against memory exhaustion.

Orchard proving can require large amounts of memory, so by default
`z_sendmany` will not attempt to create transactions containing more
than 50 Orchard inputs or outputs to reduce the risk of memory
exhaustion.  The `-orchardactionlimit` parameter allows users with
larger amounts of memory at their disposal to override this limit.

Fixes #5889

## Patch
### doc/release-notes.md
```diff
@@ -14,6 +14,12 @@ Option handling
   to specify the number of blocks back from the chain tip that anchors will be
   selected from when spending notes. By default, anchors will now be selected
   to have 3 confirmations. Values greater than 100 are not supported.
+- A new `-orchardactionlimit` option has been added to allow the user to
+  override the default maximum of 50 Orchard actions per transaction. 
+  Transactions that contain large numbers of Orchard actions can use 
+  large amounts of memory for proving, so the 50-action default limit is
+  imposed to guard against memory exhaustion. Systems with more than 16G
+  of memory can safely set this parameter to allow 200 actions or more.
 
 RPC Interface
 -------------
```

### src/wallet/asyncrpcoperation_sendmany.cpp
```diff
@@ -290,9 +290,23 @@ uint256 AsyncRPCOperation_sendmany::main_impl() {
                 "Resubmit with the `privacyPolicy` parameter set to `AllowRevealedAmounts` "
                 "or weaker if you wish to allow this transaction to proceed anyway.");
         }
+
         // Sending from Orchard to transparent will be caught above in the
         // AllowRevealedRecipients check; sending to Sprout is disallowed
         // entirely.
+
+        if (spendable.orchardNoteMetadata.size() > nOrchardActionLimit) {
+            throw JSONRPCError(
+                RPC_INVALID_PARAMETER,
+                strprintf(
+                    "Attempting to spend %u Orchard notes would exceed the current limit "
+                    "of %u notes, which exists to prevent memory exhaustion. Restart with "
+                    "`-orchardactionlimit=N` where N >= %u to allow the wallet to attempt "
+                    "to construct this transaction.",
+                    spendable.orchardNoteMetadata.size(),
+                    nOrchardActionLimit,
+                    spendable.orchardNoteMetadata.size()));
+        }
     }
 
     spendable.LogInputs(getId());
@@ -553,7 +567,6 @@ uint256 AsyncRPCOperation_sendmany::main_impl() {
             [&](const libzcash::OrchardRawAddress& addr) {
                 auto value = r.amount;
                 auto memo = r.memo.has_value() ? std::optional(get_memo_from_hex_string(r.memo.value())) : std::nullopt;
-
                 builder_.AddOrchardOutput(ovks.second, addr, value, memo);
             }
         }, r.address);
```

### src/wallet/rpcwallet.cpp
```diff
@@ -4999,6 +4999,7 @@ UniValue z_sendmany(const UniValue& params, bool fHelp)
     std::set<RecipientAddress> recipientAddrs;
     std::vector<SendManyRecipient> recipients;
     CAmount nTotalOut = 0;
+    size_t nOrchardOutputs = 0;
     for (const UniValue& o : outputs.getValues()) {
         if (!o.isObject())
             throw JSONRPCError(RPC_INVALID_PARAMETER, "Invalid parameter, expected object");
@@ -5064,6 +5065,22 @@ UniValue z_sendmany(const UniValue& params, bool fHelp)
             involvesUnifiedAddress = true;
         }
 
+        if (std::holds_alternative<libzcash::OrchardRawAddress>(addr.value())) {
+            nOrchardOutputs += 1;
+            if (nOrchardOutputs > nOrchardActionLimit) {
+                throw JSONRPCError(
+                    RPC_INVALID_PARAMETER,
+                    strprintf(
+                        "Attempting to create %u Orchard outputs would exceed the current limit "
+                        "of %u notes, which exists to prevent memory exhaustion. Restart with "
+                        "`-orchardactionlimit=N` where N >= %u to allow the wallet to attempt "
+                        "to construct this transaction.",
+                        nOrchardOutputs,
+                        nOrchardActionLimit,
+                        nOrchardOutputs));
+            }
+        }
+
         recipients.push_back(SendManyRecipient(ua, addr.value(), nAmount, memo));
         nTotalOut += nAmount;
     }
```

### src/wallet/wallet.cpp
```diff
@@ -52,6 +52,7 @@ bool bSpendZeroConfChange = DEFAULT_SPEND_ZEROCONF_CHANGE;
 bool fSendFreeTransactions = DEFAULT_SEND_FREE_TRANSACTIONS;
 bool fPayAtLeastCustomFee = true;
 unsigned int nAnchorConfirmations = DEFAULT_ANCHOR_CONFIRMATIONS;
+unsigned int nOrchardActionLimit = DEFAULT_ORCHARD_ACTION_LIMIT;
 
 const char * DEFAULT_WALLET_DAT = "wallet.dat";
 
@@ -6603,6 +6604,13 @@ bool CWallet::ParameterInteraction(const CChainParams& params)
         }
         nAnchorConfirmations = confirmations;
     }
+    if (mapArgs.count("-orchardactionlimit")) {
+        int64_t limit = atoi64(mapArgs["-orchardactionlimit"]);
+        if (limit < 1) {
+            return UIError(strprintf(_("Invalid value for -orchardactionlimit='%u' (must be least 1)"), limit));
+        }
+        nOrchardActionLimit = limit;
+    }
 
     return true;
 }
```

### src/wallet/wallet.h
```diff
@@ -54,6 +54,9 @@ extern bool bSpendZeroConfChange;
 extern bool fSendFreeTransactions;
 extern bool fPayAtLeastCustomFee;
 extern unsigned int nAnchorConfirmations;
+// The maximum number of Orchard actions permitted within a single transaction.
+// This can be overridden with the -orchardactionlimit CLI flag.
+extern unsigned int nOrchardActionLimit;
 
 static const unsigned int DEFAULT_KEYPOOL_SIZE = 100;
 //! -paytxfee default
@@ -82,6 +85,8 @@ static const size_t WALLET_MNEMONIC_ENTROPY_LENGTH = 32;
 static const unsigned int DEFAULT_ANCHOR_CONFIRMATIONS = 3;
 // Default minimum number of confirmations for note selection
 static const unsigned int DEFAULT_NOTE_CONFIRMATIONS = 10;
+//! -orchardactionlimit default
+static const unsigned int DEFAULT_ORCHARD_ACTION_LIMIT = 50;
 
 extern const char * DEFAULT_WALLET_DAT;
 
```
