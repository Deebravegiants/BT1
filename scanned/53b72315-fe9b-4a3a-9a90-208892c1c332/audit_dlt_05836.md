# [?] fix: Address permission delegation vulnerability (#5825)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2025-10-31
Source: https://github.com/XRPLF/rippled/commit/fa6991812471bdde0d771754e8b7e688d774c81f
Type: security-commit

## Details
fix: Address permission delegation vulnerability (#5825)

This change introduces the `featurePermissionDelegationV1_1` amendment, which is designed to supersede both `featurePermissionDelegation` and `fixDelegateV1_1 amendments, which should be considered deprecated. The `checkPermission` function will now return `terNO_DELEGATE_PERMISSION` when a delegate transaction lacks the necessary permissions.

## Patch
### include/xrpl/protocol/TER.h
```diff
@@ -225,8 +225,9 @@ enum TERcodes : TERUnderlyingType {
     terQUEUED,       // Transaction is being held in TxQ until fee drops
     terPRE_TICKET,   // Ticket is not yet in ledger but might be on its way
     terNO_AMM,       // AMM doesn't exist for the asset pair
-    terADDRESS_COLLISION,  // Failed to allocate AccountID when trying to
-                           // create a pseudo-account
+    terADDRESS_COLLISION,       // Failed to allocate AccountID when trying to
+                                // create a pseudo-account
+    terNO_DELEGATE_PERMISSION,  // Delegate does not have permission
 };
 
 //------------------------------------------------------------------------------
@@ -361,6 +362,9 @@ enum TECcodes : TERUnderlyingType {
     tecLIMIT_EXCEEDED = 195,
     tecPSEUDO_ACCOUNT = 196,
     tecPRECISION_LOSS = 197,
+    // DEPRECATED: This error code tecNO_DELEGATE_PERMISSION is reserved for
+    // backward compatibility with historical data on non-prod networks, can be
+    // reclaimed after those networks reset.
     tecNO_DELEGATE_PERMISSION = 198,
 };
 
```

### include/xrpl/protocol/detail/features.macro
```diff
@@ -30,11 +30,11 @@
 // Add new amendments to the top of this list.
 // Keep it sorted in reverse chronological order.
 
+XRPL_FEATURE(PermissionDelegationV1_1,   Supported::no,  VoteBehavior::DefaultNo)
 XRPL_FIX    (DirectoryLimit,             Supported::yes, VoteBehavior::DefaultNo)
 XRPL_FIX    (IncludeKeyletFields,        Supported::yes, VoteBehavior::DefaultNo)
 XRPL_FEATURE(DynamicMPT,                 Supported::no,  VoteBehavior::DefaultNo)
 XRPL_FIX    (TokenEscrowV1,              Supported::yes, VoteBehavior::DefaultNo)
-XRPL_FIX    (DelegateV1_1,               Supported::no,  VoteBehavior::DefaultNo)
 XRPL_FIX    (PriceOracleOrder,           Supported::yes, VoteBehavior::DefaultNo)
 XRPL_FIX    (MPTDeliveredAmount,         Supported::yes, VoteBehavior::DefaultNo)
 XRPL_FIX    (AMMClawbackRounding,        Supported::yes, VoteBehavior::DefaultNo)
@@ -44,7 +44,6 @@ XRPL_FIX    (AMMv1_3,                    Supported::yes, VoteBehavior::DefaultNo
 XRPL_FEATURE(PermissionedDEX,            Supported::yes, VoteBehavior::DefaultNo)
 XRPL_FEATURE(Batch,                      Supported::yes, VoteBehavior::DefaultNo)
 XRPL_FEATURE(SingleAssetVault,           Supported::no,  VoteBehavior::DefaultNo)
-XRPL_FEATURE(PermissionDelegation,       Supported::no,  VoteBehavior::DefaultNo)
 XRPL_FIX    (PayChanCancelAfter,         Supported::yes, VoteBehavior::DefaultNo)
 // Check flags in Credential transactions
 XRPL_FIX    (InvalidTxFlags,             Supported::yes, VoteBehavior::DefaultNo)
```

### include/xrpl/protocol/detail/transactions.macro
```diff
@@ -316,7 +316,7 @@ TRANSACTION(ttTRUST_SET, 20, TrustSet,
 #endif
 TRANSACTION(ttACCOUNT_DELETE, 21, AccountDelete,
     Delegation::notDelegatable,
-    uint256{},
+    featureDeletableAccounts,
     mustDeleteAcct,
     ({
     {sfDestination, soeREQUIRED},
@@ -837,7 +837,7 @@ TRANSACTION(ttPERMISSIONED_DOMAIN_DELETE, 63, PermissionedDomainDelete,
 #endif
 TRANSACTION(ttDELEGATE_SET, 64, DelegateSet,
     Delegation::notDelegatable,
-    featurePermissionDelegation,
+    featurePermissionDelegationV1_1,
     noPriv,
     ({
     {sfAuthorize, soeREQUIRED},
```

### src/libxrpl/protocol/Permissions.cpp
```diff
@@ -174,21 +174,22 @@ Permission::isDelegatable(
     auto const txType = permissionToTxType(permissionValue);
     auto const it = delegatableTx_.find(txType);
 
-    if (rules.enabled(fixDelegateV1_1))
-    {
-        if (it == delegatableTx_.end())
-            return false;
+    if (it == delegatableTx_.end())
+        return false;
 
-        auto const feature = getTxFeature(txType);
+    auto const txFeaturesIt = txFeatureMap_.find(txType);
+    XRPL_ASSERT(
+        txFeaturesIt != txFeatureMap_.end(),
+        "ripple::Permissions::isDelegatable : tx exists in txFeatureMap_");
 
-        // fixDelegateV1_1: Delegation is only allowed if the required amendment
-        // for the transaction is enabled. For transactions that do not require
-        // an amendment, delegation is always allowed.
-        if (feature && !rules.enabled(*feature))
-            return false;
-    }
+    // Delegation is only allowed if the required amendment for the transaction
+    // is enabled. For transactions that do not require an amendment, delegation
+    // is always allowed.
+    if (txFeaturesIt->second != uint256{} &&
+        !rules.enabled(txFeaturesIt->second))
+        return false;
 
-    if (it != delegatableTx_.end() && it->second == Delegation::notDelegatable)
+    if (it->second == Delegation::notDelegatable)
         return false;
 
     return true;
```

### src/libxrpl/protocol/TER.cpp
```diff
@@ -127,7 +127,6 @@ transResults()
         MAKE_ERROR(tecLIMIT_EXCEEDED,                "Limit exceeded."),
         MAKE_ERROR(tecPSEUDO_ACCOUNT,                "This operation is not allowed against a pseudo-account."),
         MAKE_ERROR(tecPRECISION_LOSS,                "The amounts used by the transaction cannot interact."),
-        MAKE_ERROR(tecNO_DELEGATE_PERMISSION,        "Delegated account lacks permission to perform this transaction."),
 
         MAKE_ERROR(tefALREADY,                     "The exact transaction was already in this ledger."),
         MAKE_ERROR(tefBAD_ADD_AUTH,                "Not authorized to add account."),
@@ -235,6 +234,7 @@ transResults()
         MAKE_ERROR(terPRE_TICKET,             "Ticket is not yet in ledger."),
         MAKE_ERROR(terNO_AMM,                 "AMM doesn't exist for the asset pair."),
         MAKE_ERROR(terADDRESS_COLLISION,      "Failed to allocate an unique account address."),
+        MAKE_ERROR(terNO_DELEGATE_PERMISSION, "Delegated account lacks permission to perform this transaction."),
 
         MAKE_ERROR(tesSUCCESS,                "The transaction was applied. Only final in a validated ledger."),
     };
```

### src/test/app/Batch_test.cpp
```diff
@@ -3946,14 +3946,13 @@ class Batch_test : public beast::unit_test::suite
                 tesSUCCESS,
                 batch::outer(gw, seq, batchFee, tfIndependent),
                 batch::inner(jv1, seq + 1),
-                // tecNO_DELEGATE_PERMISSION: not authorized to clear freeze
+                // terNO_DELEGATE_PERMISSION: not authorized to clear freeze
                 batch::inner(jv2, seq + 2));
             env.close();
 
             std::vector<TestLedgerData> testCases = {
                 {0, "Batch", "tesSUCCESS", batchID, std::nullopt},
                 {1, "TrustSet", "tesSUCCESS", txIDs[0], batchID},
-                {2, "TrustSet", "tecNO_DELEGATE_PERMISSION", txIDs[1], batchID},
             };
             validateClosedLedger(env, testCases);
         }
```

### src/test/app/Delegate_test.cpp
```diff
@@ -27,23 +27,27 @@ namespace test {
 class Delegate_test : public beast::unit_test::suite
 {
     void
-    testFeatureDisabled()
+    testFeatureDisabled(FeatureBitset features)
     {
-        testcase("test featurePermissionDelegation not enabled");
+        testcase("test feature not enabled");
         using namespace jtx;
 
-        Env env{*this, testable_amendments() - featurePermissionDelegation};
+        Env env{*this, features};
         Account gw{"gateway"};
         Account alice{"alice"};
         Account bob{"bob"};
         env.fund(XRP(1000000), gw, alice, bob);
         env.close();
 
+        auto res = features[featurePermissionDelegationV1_1] ? ter(tesSUCCESS)
+                                                             : ter(temDISABLED);
+
         // can not set Delegate when feature disabled
-        env(delegate::set(gw, alice, {"Payment"}), ter(temDISABLED));
+        env(delegate::set(gw, alice, {"Payment"}), res);
+        env.close();
 
         // can not send delegating transaction when feature disabled
-        env(pay(alice, bob, XRP(100)), delegate::as(bob), ter(temDISABLED));
+        env(pay(gw, bob, XRP(100)), delegate::as(alice), res);
     }
 
     void
@@ -217,17 +221,16 @@ class Delegate_test : public beast::unit_test::suite
         }
 
         // non-delegatable transaction
-        auto const res = features[fixDelegateV1_1] ? ter(temMALFORMED)
-                                                   : ter(tecNO_PERMISSION);
         {
-            env(delegate::set(gw, alice, {"SetRegularKey"}), res);
-            env(delegate::set(gw, alice, {"AccountSet"}), res);
-            env(delegate::set(gw, alice, {"SignerListSet"}), res);
-            env(delegate::set(gw, alice, {"DelegateSet"}), res);
-            env(delegate::set(gw, alice, {"EnableAmendment"}), res);
-            env(delegate::set(gw, alice, {"UNLModify"}), res);
-            env(delegate::set(gw, alice, {"SetFee"}), res);
-            env(delegate::set(gw, alice, {"Batch"}), res);
+            env(delegate::set(gw, alice, {"SetRegularKey"}), ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"AccountSet"}), ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"SignerListSet"}), ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"DelegateSet"}), ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"EnableAmendment"}),
+                ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"UNLModify"}), ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"SetFee"}), ter(temMALFORMED));
+            env(delegate::set(gw, alice, {"Batch"}), ter(temMALFORMED));
         }
     }
 
@@ -305,18 +308,14 @@ class Delegate_test : public beast::unit_test::suite
         env.close();
 
         {
-            // Fee should be checked before permission check,
-            // otherwise tecNO_DELEGATE_PERMISSION returned when permission
-            // check fails could cause context reset to pay fee because it is
-            // tec error
             auto aliceBalance = env.balance(alice);
             auto bobBalance = env.balance(bob);
             auto carolBalance = env.balance(carol);
 
             env(pay(alice, carol, XRP(100)),
                 fee(XRP(2000)),
                 delegate::as(bob),
-                ter(terINSUF_FEE_B));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
             BEAST_EXPECT(env.balance(alice) == aliceBalance);
             BEAST_EXPECT(env.balance(bob) == bobBalance);
@@ -523,12 +522,12 @@ class Delegate_test : public beast::unit_test::suite
         // bob does not have permission to create check
         env(check::create(alice, bob, XRP(10)),
             delegate::as(bob),
-            ter(tecNO_DELEGATE_PERMISSION));
+            ter(terNO_DELEGATE_PERMISSION));
 
         // carol does not have permission to create check
         env(check::create(alice, bob, XRP(10)),
             delegate::as(carol),
-            ter(tecNO_DELEGATE_PERMISSION));
+            ter(terNO_DELEGATE_PERMISSION));
     }
 
     void
@@ -563,9 +562,8 @@ class Delegate_test : public beast::unit_test::suite
             // delegate ledger object is not created yet
             env(pay(gw, alice, USD(50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
-            env.require(balance(bob, bobBalance - drops(baseFee)));
-            bobBalance = env.balance(bob, XRP);
+                ter(terNO_DELEGATE_PERMISSION));
+            env.require(balance(bob, bobBalance));
 
             // gw gives bob burn permission
             env(delegate::set(gw, bob, {"PaymentBurn"}));
@@ -576,10 +574,9 @@ class Delegate_test : public beast::unit_test::suite
             // bob sends a payment transaction on behalf of gw
             env(pay(gw, alice, USD(50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
-            env.require(balance(bob, bobBalance - drops(baseFee)));
-            bobBalance = env.balance(bob, XRP);
+            env.require(balance(bob, bobBalance));
 
             // gw gives bob mint permission, alice gives bob burn permission
             env(delegate::set(gw, bob, {"PaymentMint"}));
@@ -593,10 +590,9 @@ class Delegate_test : public beast::unit_test::suite
             // can not send XRP
             env(pay(gw, alice, XRP(50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
-            env.require(balance(bob, bobBalance - drops(baseFee)));
-            bobBalance = env.balance(bob, XRP);
+            env.require(balance(bob, bobBalance));
 
             // mint 50 USD
             env(pay(gw, alice, USD(50)), delegate::as(bob));
@@ -681,10 +677,9 @@ class Delegate_test : public beast::unit_test::suite
             // permission
             env(pay(gw, alice, USD(50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
-            env.require(balance(bob, bobBalance - drops(baseFee)));
-            bobBalance = env.balance(bob, XRP);
+            env.require(balance(bob, bobBalance));
 
             // gw gives bob Payment permission as well
             env(delegate::set(gw, bob, {"PaymentBurn", "Payment"}));
@@ -723,28 +718,28 @@ class Delegate_test : public beast::unit_test::suite
             env(pay(gw, carol, USD(10000)));
             env.close();
 
-            auto const result = features[fixDelegateV1_1]
-                ? static_cast<TER>(tecNO_DELEGATE_PERMISSION)
-                : static_cast<TER>(tesSUCCESS);
-            auto const offerCount = features[fixDelegateV1_1] ? 1 : 0;
-
             // PaymentMint
             {
                 env(offer(carol, XRP(100), USD(501)));
                 BEAST_EXPECT(expectOffers(env, carol, 1));
                 env(delegate::set(gw, bob, {"PaymentMint"}));
                 env.close();
 
-                // post-amendment: fixDelegateV1_1
                 // bob can not send cross currency payment on behalf of the gw,
                 // even with PaymentMint permission and gw being the issuer.
                 env(pay(gw, alice, USD(5000)),
-                    path(~USD),
                     sendmax(XRP(1001)),
                     txflags(tfPartialPayment),
                     delegate::as(bob),
-                    ter(result));
-                BEAST_EXPECT(expectOffers(env, carol, offerCount));
+                    ter(terNO_DELEGATE_PERMISSION));
+                BEAST_EXPECT(expectOffers(env, carol, 1));
+
+                env(pay(gw, alice, USD(5000)),
+                    path(~XRP),
+                    txflags(tfPartialPayment),
+                    delegate::as(bob),
+                    ter(terNO_DELEGATE_PERMISSION));
+                BEAST_EXPECT(expectOffers(env, carol, 1));
 
                 // succeed with direct payment
                 env(pay(gw, alice, USD(100)), delegate::as(bob));
@@ -758,16 +753,21 @@ class Delegate_test : public beast::unit_test::suite
                 env(delegate::set(alice, bob, {"PaymentBurn"}));
                 env.close();
 
-                // post-amendment: fixDelegateV1_1
                 // bob can not send cross currency payment on behalf of alice,
                 // even with PaymentBurn permission and gw being the issuer.
                 env(pay(alice, gw, USD(5000)),
-                    path(~USD),
                     sendmax(XRP(1001)),
                     txflags(tfPartialPayment),
                     delegate::as(bob),
-                    ter(result));
-                BEAST_EXPECT(expectOffers(env, bob, offerCount));
+                    ter(terNO_DELEGATE_PERMISSION));
+                BEAST_EXPECT(expectOffers(env, bob, 1));
+
+                env(pay(alice, gw, USD(5000)),
+                    path(~XRP),
+                    txflags(tfPartialPayment),
+                    delegate::as(bob),
+                    ter(terNO_DELEGATE_PERMISSION));
+                BEAST_EXPECT(expectOffers(env, bob, 1));
 
                 // succeed with direct payment
                 env(pay(alice, gw, USD(100)), delegate::as(bob));
@@ -802,45 +802,24 @@ class Delegate_test : public beast::unit_test::suite
                 env(delegate::set(gw, bob, {"PaymentMint"}));
                 env.close();
 
-                if (!features[fixDelegateV1_1])
-                {
-                    // pre-amendment: PaymentMint is not supported for MPT
-                    env(pay(gw, alice, MPT(50)),
-                        delegate::as(bob),
-                        ter(tefEXCEPTION));
-                }
-                else
-                {
-                    env(pay(gw, alice, MPT(50)), delegate::as(bob));
-                    BEAST_EXPECT(env.balance(alice, MPT) == aliceMPT + MPT(50));
-                    BEAST_EXPECT(env.balance(bob, MPT) == bobMPT);
-                    aliceMPT = env.balance(alice, MPT);
-                }
+                env(pay(gw, alice, MPT(50)), delegate::as(bob));
+                BEAST_EXPECT(env.balance(alice, MPT) == aliceMPT + MPT(50));
+                BEAST_EXPECT(env.balance(bob, MPT) == bobMPT);
+                aliceMPT = env.balance(alice, MPT);
             }
 
             // PaymentBurn
             {
                 env(delegate::set(alice, bob, {"PaymentBurn"}));
                 env.close();
 
-                if (!features[fixDelegateV1_1])
-                {
-                    // pre-amendment: PaymentBurn is not supported for MPT
-                    env(pay(alice, gw, MPT(50)),
-                        delegate::as(bob),
-                        ter(tefEXCEPTION));
-                }
-                else
-                {
-                    env(pay(alice, gw, MPT(50)), delegate::as(bob));
-                    BEAST_EXPECT(env.balance(alice, MPT) == aliceMPT - MPT(50));
-                    BEAST_EXPECT(env.balance(bob, MPT) == bobMPT);
-                    aliceMPT = env.balance(alice, MPT);
-                }
+                env(pay(alice, gw, MPT(50)), delegate::as(bob));
+                BEAST_EXPECT(env.balance(alice, MPT) == aliceMPT - MPT(50));
+                BEAST_EXPECT(env.balance(bob, MPT) == bobMPT);
+                aliceMPT = env.balance(alice, MPT);
             }
 
-            // Payment transaction for MPT is allowed for both pre and post
-            // amendment
+            // Grant both granular permissions and tx level permission.
             {
                 env(delegate::set(
                     alice, bob, {"PaymentBurn", "PaymentMint", "Payment"}));
@@ -878,7 +857,7 @@ class Delegate_test : public beast::unit_test::suite
             // has unfreeze permission
             env(trust(alice, gw["USD"](50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
 
             // alice creates trustline by herself
@@ -892,38 +871,38 @@ class Delegate_test : public beast::unit_test::suite
             // unsupported flags
             env(trust(alice, gw["USD"](50), tfSetNoRipple),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(trust(alice, gw["USD"](50), tfClearNoRipple),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(trust(gw, gw["USD"](0), alice, tfSetDeepFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(trust(gw, gw["USD"](0), alice, tfClearDeepFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
 
             // supported flags with wrong permission
             env(trust(gw, gw["USD"](0), alice, tfSetfAuth),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(trust(gw, gw["USD"](0), alice, tfSetFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
 
             env(delegate::set(gw, bob, {"TrustlineAuthorize"}));
             env.close();
             env(trust(gw, gw["USD"](0), alice, tfClearFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
             // although trustline authorize is granted, bob can not change the
             // limit number
             env(trust(gw, gw["USD"](50), alice, tfSetfAuth),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env.close();
 
             // supported flags with correct permission
@@ -944,30 +923,30 @@ class Delegate_test : public beast::unit_test::suite
             // permission
             env(trust(gw, gw["USD"](0), alice, tfSetFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // cannot update LimitAmount with granular permission, both high and
             // low account
             env(trust(alice, gw["USD"](100)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(trust(gw, alice["USD"](100)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // can not set QualityIn or QualityOut
             auto tx = trust(alice, gw["USD"](50));
             tx["QualityIn"] = "1000";
-            env(tx, delegate::as(bob), ter(tecNO_DELEGATE_PERMISSION));
+            env(tx, delegate::as(bob), ter(terNO_DELEGATE_PERMISSION));
             auto tx2 = trust(alice, gw["USD"](50));
             tx2["QualityOut"] = "1000";
-            env(tx2, delegate::as(bob), ter(tecNO_DELEGATE_PERMISSION));
+            env(tx2, delegate::as(bob), ter(terNO_DELEGATE_PERMISSION));
             auto tx3 = trust(gw, alice["USD"](50));
             tx3["QualityIn"] = "1000";
-            env(tx3, delegate::as(bob), ter(tecNO_DELEGATE_PERMISSION));
+            env(tx3, delegate::as(bob), ter(terNO_DELEGATE_PERMISSION));
             auto tx4 = trust(gw, alice["USD"](50));
             tx4["QualityOut"] = "1000";
-            env(tx4, delegate::as(bob), ter(tecNO_DELEGATE_PERMISSION));
+            env(tx4, delegate::as(bob), ter(terNO_DELEGATE_PERMISSION));
 
             // granting TrustSet can make it work
             env(delegate::set(gw, bob, {"TrustSet"}));
@@ -977,7 +956,7 @@ class Delegate_test : public beast::unit_test::suite
             env(tx5, delegate::as(bob));
             auto tx6 = trust(alice, gw["USD"](50));
             tx6["QualityOut"] = "1000";
-            env(tx6, delegate::as(bob), ter(tecNO_DELEGATE_PERMISSION));
+            env(tx6, delegate::as(bob), ter(terNO_DELEGATE_PERMISSION));
             env(delegate::set(alice, bob, {"TrustSet"}));
             env.close();
             env(tx6, delegate::as(bob));
@@ -996,14 +975,14 @@ class Delegate_test : public beast::unit_test::suite
             // bob does not have permission
             env(trust(alice, gw["USD"](50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(delegate::set(
                 alice, bob, {"TrustlineUnfreeze", "NFTokenCreateOffer"}));
             env.close();
             // bob still does not have permission
             env(trust(alice, gw["USD"](50)),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // add TrustSet permission and some unrelated permission
             env(delegate::set(
@@ -1096,7 +1075,7 @@ class Delegate_test : public beast::unit_test::suite
             env(delegate::set(
                 alice, bob, {"TrustlineUnfreeze", "AccountEmailHashSet"}));
             env.close();
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
 
             // alice give granular permission of AccountDomainSet to bob
             env(delegate::set(alice, bob, {"AccountDomainSet"}));
@@ -1115,7 +1094,7 @@ class Delegate_test : public beast::unit_test::suite
             std::string const failDomain = "fail_domain_update";
             jt[sfFlags] = tfRequireAuth;
             jt[sfDomain] = strHex(failDomain);
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
             // reset flag number
             jt[sfFlags] = 0;
 
@@ -1124,7 +1103,7 @@ class Delegate_test : public beast::unit_test::suite
             jt[sfDomain] = strHex(domain);
             std::string const mh("5F31A79367DC3137FADA860C05742EE6");
             jt[sfEmailHash] = mh;
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
 
             // alice give granular permission of AccountEmailHashSet to bob
             env(delegate::set(
@@ -1137,7 +1116,7 @@ class Delegate_test : public beast::unit_test::suite
             // bob does not have permission to set message key for alice
             auto const rkp = randomKeyPair(KeyType::ed25519);
             jt[sfMessageKey] = strHex(rkp.first.slice());
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
 
             // alice give granular permission of AccountMessageKeySet to bob
             env(delegate::set(
@@ -1160,7 +1139,7 @@ class Delegate_test : public beast::unit_test::suite
             // bob does not have permission to set transfer rate for alice
             env(rate(alice, 2.0),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // alice give granular permission of AccountTransferRateSet to bob
             env(delegate::set(
@@ -1178,7 +1157,7 @@ class Delegate_test : public beast::unit_test::suite
 
             // bob does not have permission to set ticksize for alice
             jt[sfTickSize] = 8;
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
 
             // alice give granular permission of AccountTickSizeSet to bob
             env(delegate::set(
@@ -1196,7 +1175,7 @@ class Delegate_test : public beast::unit_test::suite
             // can not set asfRequireAuth flag for alice
             env(fset(alice, asfRequireAuth),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // reset Delegate will delete the Delegate
             // object
@@ -1205,15 +1184,15 @@ class Delegate_test : public beast::unit_test::suite
             // alice
             env(fset(alice, asfRequireAuth),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             // alice can set for herself
             env(fset(alice, asfRequireAuth));
             env.require(flags(alice, asfRequireAuth));
             env.close();
 
             // can not update tick size because bob no longer has permission
             jt[sfTickSize] = 7;
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
 
             env(delegate::set(
                 alice,
@@ -1231,7 +1210,7 @@ class Delegate_test : public beast::unit_test::suite
             jv2[sfDomain] = strHex(domain);
             jv2[sfDelegate] = bob.human();
             jv2[sfWalletLocator] = locator;
-            env(jv2, ter(tecNO_DELEGATE_PERMISSION));
+            env(jv2, ter(terNO_DELEGATE_PERMISSION));
         }
 
         // can not set AccountSet flags on behalf of other account
@@ -1246,15 +1225,15 @@ class Delegate_test : public beast::unit_test::suite
                 // bob can not set flag on behalf of alice
                 env(fset(alice, flag),
                     delegate::as(bob),
-                    ter(tecNO_DELEGATE_PERMISSION));
+                    ter(terNO_DELEGATE_PERMISSION));
                 // alice set by herself
                 env(fset(alice, flag));
                 env.close();
                 env.require(flags(alice, flag));
                 // bob can not clear on behalf of alice
                 env(fclear(alice, flag),
                     delegate::as(bob),
-                    ter(tecNO_DELEGATE_PERMISSION));
+                    ter(terNO_DELEGATE_PERMISSION));
             };
 
             // testSetClearFlag(asfNoFreeze);
@@ -1283,19 +1262,19 @@ class Delegate_test : public beast::unit_test::suite
             // bob can not set asfAccountTxnID on behalf of alice
             env(fset(alice, asfAccountTxnID),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(fset(alice, asfAccountTxnID));
             env.close();
             BEAST_EXPECT(env.le(alice)->isFieldPresent(sfAccountTxnID));
             env(fclear(alice, asfAccountTxnID),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // bob can not set asfAuthorizedNFTokenMinter on behalf of alice
             Json::Value jt = fset(alice, asfAuthorizedNFTokenMinter);
             jt[sfDelegate] = bob.human();
             jt[sfNFTokenMinter] = bob.human();
-            env(jt, ter(tecNO_DELEGATE_PERMISSION));
+            env(jt, ter(terNO_DELEGATE_PERMISSION));
 
             // bob gives alice some permissions
             env(delegate::set(
@@ -1311,14 +1290,14 @@ class Delegate_test : public beast::unit_test::suite
             // behalf of bob.
             env(fset(alice, asfNoFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
             env(fset(bob, asfNoFreeze));
             env.close();
             env.require(flags(bob, asfNoFreeze));
             // alice can not clear on behalf of bob
             env(fclear(alice, asfNoFreeze),
                 delegate::as(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
 
             // bob can not set asfDisableMaster on behalf of alice
             Account const bobKey{"bobKey", KeyType::secp256k1};
@@ -1327,7 +1306,7 @@ class Delegate_test : public beast::unit_test::suite
             env(fset(alice, asfDisableMaster),
                 delegate::as(bob),
                 sig(bob),
-                ter(tecNO_DELEGATE_PERMISSION));
+                ter(terNO_DELEGATE_PERMISSION));
         }
 
         // tfFullyCanonicalSig won't block delegated transaction
@@ -1377,7 +1356,7 @@ class Delegate_test : public beast::unit_test::suite
                 {.account = alice,
                  .flags = tfMPTLock,
                  .delegate = bob,
-                 .err = tecNO_DELEGATE_PERMISSION});
+                 .err = terNO_DELEGATE_PERMISSION});
 
             // alice gives granular permission to bob of MPTokenIssuanceUnlock
             env(delegate::set(alice, bob, {"MPTokenIssuanceUnlock"}));
@@ -1387,7 +1366,7 @@ class Delegate_test : public beast::unit_test::suite
                 {.account = alice,
                  .flags = tfMPTLock,
                  .delegate = bob,
-                 .err = tecNO_DELEGATE_PERMISSION});
+                 .err = terNO_DELEGATE_PERMISSION});
             // bob now has lock permission, but does not have unlock permission
             env(delegate::set(alice, bob, {"MPTokenIssuanceLock"}));
             env.close();
@@ -1396,7 +1375,7 @@ class Delegate_test : public beast::unit_test::suite
                 {.account = alice,
                  .flags = tfMPTUnlock,
                  .delegate = bob,
-                 .err = tecNO_DELEGATE_PERMISSION});
+                 .err = terNO_DELEGATE_PERMISSION});
 
             // now bob can lock and unlock
             env(delegate::set(
@@ -1429,7 +1408,7 @@ class Delegate_test : public beast::unit_test::suite
                 {.account = alice,
                  .flags = tfMPTUnlock,
                  .delegate = bob,
-                 .err = tecNO_DELEGATE_PERMISSION});
+                 .err = terNO_DELEGATE_PERMISSION});
 
             // alice gives bob some unrelated permission with
             // MPTokenIssuanceLock
@@ -1443,7 +1422,7 @@ class Delegate_test : public beast::unit_test::suite
                 {.account = alice,
                  .flags = tfMPTUnlock,
                  .delegate = bob,
-                 .err = tecNO_DELEGATE_PERMISSION});
+                 .err = terNO_DELEGATE_PERMISSION});
 
             // alice add MPTokenIssuanceSet to permissions
             env(delegate::set(
@@ -1519,29 +1498,96 @@ class Delegate_test : public beast::unit_test::suite
         testcase("test single sign with bad secret");
         using namespace jtx;
 
-        Env env(*this);
-        Account alice{"alice"};
-        Account bob{"bob"};
-        Account carol{"carol"};
-        env.fund(XRP(100000), alice, bob, carol);
-        env.close();
+        {
+            Env env(*this);
+            Account alice{"alice"};
+            Account bob{"bob"};
+            Account carol{"carol"};
+            env.fund(XRP(100000), alice, bob, carol);
+            env.close();
 
-        env(delegate::set(alice, bob, {"Payment"}));
-        env.close();
+            env(delegate::set(alice, bob, {"Payment"}));
+            env.close();
 
-        auto aliceBalance = env.balance(alice);
-        auto bobBalance = env.balance(bob);
-        auto carolBalance = env.balance(carol);
+            auto aliceBalance = env.balance(alice);
+            auto bobBalance = env.balance(bob);
+            auto carolBalance = env.balance(carol);
 
-        env(pay(alice, carol, XRP(100)),
-            fee(XRP(10)),
-            delegate::as(bob),
-            sig(alice),
-            ter(tefBAD_AUTH));
-        env.close();
-        BEAST_EXPECT(env.balance(alice) == aliceBalance);
-        BEAST_EXPECT(env.balance(bob) == bobBalance);
-        BEAST_EXPECT(env.balance(carol) == carolBalance);
+            env(pay(alice, carol, XRP(100)),
+                fee(XRP(10)),
+                delegate::as(bob),
+                sig(alice),
+                ter(tefBAD_AUTH));
+            env.close();
+            BEAST_EXPECT(env.balance(alice) == aliceBalance);
+            BEAST_EXPECT(env.balance(bob) == bobBalance);
+            BEAST_EXPECT(env.balance(carol) == carolBalance);
+        }
+
+        {
+            Env env(*this);
+            Account alice{"alice"}, bob{"bob"}, carol{"carol"};
+            env.fund(XRP(100000), alice, bob, carol);
+            env.close();
+
+            env(delegate::set(alice, bob, {"TrustSet"}));
+            env.close();
+
+            auto aliceBalance = env.balance(alice);
+            auto bobBalance = env.balance(bob);
+            auto carolBalance = env.balance(carol);
+
+            env(pay(alice, carol, XRP(100)),
+                fee(XRP(10)),
+                delegate::as(bob),
+                sig(carol),
+                ter(terNO_DELEGATE_PERMISSION));
+            env.close();
+            BEAST_EXPECT(env.balance(alice) == aliceBalance);
+            BEAST_EXPECT(env.balance(bob) == bobBalance);
+            BEAST_EXPECT(env.balance(carol) == carolBalance);
+
+            env(pay(alice, carol, XRP(100)),
+                fee(XRP(10)),
+                delegate::as(bob),
+                sig(alice),
+                ter(terNO_DELEGATE_PERMISSION));
+            env.close();
+            BEAST_EXPECT(env.balance(alice) == aliceBalance);
+            BEAST_EXPECT(env.balance(bob) == bobBalance);
+            BEAST_EXPECT(env.balance(carol) == carolBalance);
+        }
+
+        {
+            Env env(*this);
+            Account alice{"alice"}, bob{"bob"}, carol{"carol"};
+            env.fund(XRP(100000), alice, bob, carol);
+            env.close();
+
+            auto aliceBalance = env.balance(alice);
+            auto bobBalance = env.balance(bob);
+            auto carolBalance = env.balance(carol);
+
+            env(pay(alice, carol, XRP(100)),
+                fee(XRP(10)),
+                delegate::as(bob),
+                sig(alice),
+                ter(terNO_DELEGATE_PERMISSION));
+            env.close();
+            BEAST_EXPECT(env.balance(alice) == aliceBalance);
+            BEAST_EXPECT(env.balance(bob) == bobBalance);
+            BEAST_EXPECT(env.balance(carol) == carolBalance);
+
+            env(pay(alice, carol, XRP(100)),
+                fee(XRP(10)),
+                delegate::as(bob),
+                sig(carol),
+                ter(terNO_DELEGATE_PERMISSION));
+            env.close();
+            BEAST_EXPECT(env.balance(alice) == aliceBalance);
+            BEAST_EXPECT(env.balance(bob) == bobBalance);
+            BEAST_EXPECT(env.balance(carol) == carolBalance);
+        }
     }
 
     void
@@ -1659,10 +1705,7 @@ class Delegate_test : public beast::unit_test::suite
         for (auto value : {0, 100000, 54321})
         {
             auto jv = buildRequest(value);
-            if (!features[fixDelegateV1_1])
-                env(jv);
-            else
-                env(jv, ter(temMALFORMED));
+            env(jv, ter(temMALFORMED));
         }
     }
 
@@ -1720,8 +1763,7 @@ class Delegate_test : public beast::unit_test::suite
             {"VaultWithdraw", featureSingleAssetVault},
             {"VaultClawback", featureSingleAssetVault}};
 
-        // fixDelegateV1_1 post-amendment: can not delegate tx if any
-        // required feature disabled.
+        // Can not delegate tx if any required feature disabled.
         {
             auto txAmendmentDisabled = [&](FeatureBitset features,
                                            std::string const& tx) {
@@ -1734,10 +1776,7 @@ class Delegate_test : public beast::unit_test::suite
                 env.fund(XRP(100000), alice, bob);
                 env.close();
 
-                if (!features[fixDelegateV1_1])
-                    env(delegate::set(alice, bob, {tx}));
-                else
-                    env(delegate::set(alice, bob, {tx}), ter(temMALFORMED));
+                env(delegate::set(alice, bob, {tx}), ter(temMALFORMED));
             };
 
             for (auto const& tx : txRequiredFeatures)
@@ -1786,10 +1825,7 @@ class Delegate_test : public beast::unit_test::suite
                   "NFTokenCancelOffer",
                   "NFTokenAcceptOffer"})
             {
-                if (!features[fixDelegateV1_1])
-                    env(delegate::set(alice, bob, {tx}));
-                else
-                    env(delegate::set(alice, bob, {tx}), ter(temMALFORMED));
+                env(delegate::set(alice, bob, {tx}), ter(temMALFORMED));
             }
         }
 
@@ -1823,17 +1859,16 @@ class Delegate_test : public beast::unit_test::suite
     {
         FeatureBitset const all = jtx::testable_amendments();
 
-        testFeatureDisabled();
+        testFeatureDisabled(all - featurePermissionDelegationV1_1);
+        testFeatureDisabled(all);
         testDelegateSet();
         testInvalidRequest(all);
-        testInvalidRequest(all - fixDelegateV1_1);
         testReserve();
         testFee();
         testSequence();
         testAccountDelete();
         testDelegateTransaction();
         testPaymentGranular(all);
-        testPaymentGranular(all - fixDelegateV1_1);
         testTrustSetGranular();
         testAccountSetGranular();
         testMPTokenIssuanceSetGranular();
@@ -1842,9 +1877,7 @@ class Delegate_test : public beast::unit_test::suite
         testMultiSign();
         testMultiSignQuorumNotMet();
         testPermissionValue(all);
-        testPermissionValue(all - fixDelegateV1_1);
         testTxReqireFeatures(all);
-        testTxReqireFeatures(all - fixDelegateV1_1);
     }
 };
 BEAST_DEFINE_TESTSUITE(Delegate, app, ripple);
```

### src/xrpld/app/misc/DelegateUtils.h
```diff
@@ -31,10 +31,10 @@ namespace ripple {
  * Check if the delegate account has permission to execute the transaction.
  * @param delegate The delegate account.
  * @param tx The transaction that the delegate account intends to execute.
- * @return tesSUCCESS if the transaction is allowed, tecNO_DELEGATE_PERMISSION
+ * @return tesSUCCESS if the transaction is allowed, terNO_DELEGATE_PERMISSION
  * if not.
  */
-TER
+NotTEC
 checkTxPermission(std::shared_ptr<SLE const> const& delegate, STTx const& tx);
 
 /**
```

### src/xrpld/app/misc/detail/DelegateUtils.cpp
```diff
@@ -22,11 +22,11 @@
 #include <xrpl/protocol/STArray.h>
 
 namespace ripple {
-TER
+NotTEC
 checkTxPermission(std::shared_ptr<SLE const> const& delegate, STTx const& tx)
 {
     if (!delegate)
-        return tecNO_DELEGATE_PERMISSION;  // LCOV_EXCL_LINE
+        return terNO_DELEGATE_PERMISSION;  // LCOV_EXCL_LINE
 
     auto const permissionArray = delegate->getFieldArray(sfPermissions);
     auto const txPermission = tx.getTxnType() + 1;
@@ -38,7 +38,7 @@ checkTxPermission(std::shared_ptr<SLE const> const& delegate, STTx const& tx)
             return tesSUCCESS;
     }
 
-    return tecNO_DELEGATE_PERMISSION;
+    return terNO_DELEGATE_PERMISSION;
 }
 
 void
```

### src/xrpld/app/tx/detail/DelegateSet.cpp
```diff
@@ -45,8 +45,7 @@ DelegateSet::preflight(PreflightContext const& ctx)
         if (!permissionSet.insert(permission[sfPermissionValue]).second)
             return temMALFORMED;
 
-        if (ctx.rules.enabled(fixDelegateV1_1) &&
-            !Permission::getInstance().isDelegatable(
+        if (!Permission::getInstance().isDelegatable(
                 permission[sfPermissionValue], ctx.rules))
             return temMALFORMED;
     }
@@ -63,26 +62,6 @@ DelegateSet::preclaim(PreclaimContext const& ctx)
     if (!ctx.view.exists(keylet::account(ctx.tx[sfAuthorize])))
         return tecNO_TARGET;
 
-    auto const& permissions = ctx.tx.getFieldArray(sfPermissions);
-    for (auto const& permission : permissions)
-    {
-        if (!ctx.view.rules().enabled(fixDelegateV1_1) &&
-            !Permission::getInstance().isDelegatable(
-                permission[sfPermissionValue], ctx.view.rules()))
-        {
-            // Before fixDelegateV1_1:
-            //   - The check was performed during preclaim.
-            //   - Transactions from amendments not yet enabled could still be
-            //   delegated.
-            //
-            // After fixDelegateV1_1:
-            //   - The check is performed during preflight.
-            //   - Transactions from amendments not yet enabled can no longer be
-            //   delegated.
-            return tecNO_PERMISSION;
-        }
-    }
-
     return tesSUCCESS;
 }
 
```

### src/xrpld/app/tx/detail/MPTokenIssuanceSet.cpp
```diff
@@ -140,7 +140,7 @@ MPTokenIssuanceSet::preflight(PreflightContext const& ctx)
     return tesSUCCESS;
 }
 
-TER
+NotTEC
 MPTokenIssuanceSet::checkPermission(ReadView const& view, STTx const& tx)
 {
     auto const delegate = tx[~sfDelegate];
@@ -151,7 +151,7 @@ MPTokenIssuanceSet::checkPermission(ReadView const& view, STTx const& tx)
     auto const sle = view.read(delegateKey);
 
     if (!sle)
-        return tecNO_DELEGATE_PERMISSION;
+        return terNO_DELEGATE_PERMISSION;
 
     if (checkTxPermission(sle, tx) == tesSUCCESS)
         return tesSUCCESS;
@@ -161,18 +161,18 @@ MPTokenIssuanceSet::checkPermission(ReadView const& view, STTx const& tx)
     // this is added in case more flags will be added for MPTokenIssuanceSet
     // in the future. Currently unreachable.
     if (txFlags & tfMPTokenIssuanceSetPermissionMask)
-        return tecNO_DELEGATE_PERMISSION;  // LCOV_EXCL_LINE
+        return terNO_DELEGATE_PERMISSION;  // LCOV_EXCL_LINE
 
     std::unordered_set<GranularPermissionType> granularPermissions;
     loadGranularPermission(sle, ttMPTOKEN_ISSUANCE_SET, granularPermissions);
 
     if (txFlags & tfMPTLock &&
         !granularPermissions.contains(MPTokenIssuanceLock))
-        return tecNO_DELEGATE_PERMISSION;
+        return terNO_DELEGATE_PERMISSION;
 
     if (txFlags & tfMPTUnlock &&
         !granularPermissions.contains(MPTokenIssuanceUnlock))
-        return tecNO_DELEGATE_PERMISSION;
+        return terNO_DELEGATE_PERMISSION;
 
     return tesSUCCESS;
 }
```

### src/xrpld/app/tx/detail/MPTokenIssuanceSet.h
```diff
@@ -42,7 +42,7 @@ class MPTokenIssuanceSet : public Transactor
     static NotTEC
     preflight(PreflightContext const& ctx);
 
-    static TER
+    static NotTEC
     checkPermission(ReadView const& view, STTx const& tx);
 
     static TER
```
