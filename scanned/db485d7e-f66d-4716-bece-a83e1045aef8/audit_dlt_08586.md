# [?] Fix ledger_entry crash on invalid credentials request (#5189)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2024-11-12
Source: https://github.com/XRPLF/rippled/commit/2316d843d7f9bc6963b3519f4464913c27eb7335
Type: security-commit

## Details
Fix ledger_entry crash on invalid credentials request (#5189)

## Patch
### src/test/rpc/LedgerRPC_test.cpp
```diff
@@ -26,6 +26,7 @@
 #include <xrpld/app/misc/TxQ.h>
 #include <xrpl/basics/StringUtilities.h>
 #include <xrpl/beast/unit_test.h>
+#include <xrpl/json/json_value.h>
 #include <xrpl/protocol/AccountID.h>
 #include <xrpl/protocol/ErrorCodes.h>
 #include <xrpl/protocol/STXChainBridge.h>
@@ -1207,6 +1208,42 @@ class LedgerRPC_test : public beast::unit_test::suite
             checkErrorValue(jrr[jss::result], "malformedRequest", "");
         }
 
+        {
+            // Failed, authorized_credentials contains string data
+            Json::Value jvParams;
+            jvParams[jss::ledger_index] = jss::validated;
+            jvParams[jss::deposit_preauth][jss::owner] = bob.human();
+            jvParams[jss::deposit_preauth][jss::authorized_credentials] =
+                Json::arrayValue;
+            auto& arr(
+                jvParams[jss::deposit_preauth][jss::authorized_credentials]);
+            arr.append("foobar");
+
+            auto const jrr =
+                env.rpc("json", "ledger_entry", to_string(jvParams));
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
+        }
+
+        {
+            // Failed, authorized_credentials contains arrays
+            Json::Value jvParams;
+            jvParams[jss::ledger_index] = jss::validated;
+            jvParams[jss::deposit_preauth][jss::owner] = bob.human();
+            jvParams[jss::deposit_preauth][jss::authorized_credentials] =
+                Json::arrayValue;
+            auto& arr(
+                jvParams[jss::deposit_preauth][jss::authorized_credentials]);
+            Json::Value payload = Json::arrayValue;
+            payload.append(42);
+            arr.append(std::move(payload));
+
+            auto const jrr =
+                env.rpc("json", "ledger_entry", to_string(jvParams));
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
+        }
+
         {
             // Failed, authorized_credentials is empty array
             Json::Value jvParams;
@@ -1263,6 +1300,27 @@ class LedgerRPC_test : public beast::unit_test::suite
                 jrr[jss::result], "malformedAuthorizedCredentials", "");
         }
 
+        {
+            // Failed, issuer is not set
+            Json::Value jvParams;
+            jvParams[jss::ledger_index] = jss::validated;
+            jvParams[jss::deposit_preauth][jss::owner] = bob.human();
+
+            jvParams[jss::deposit_preauth][jss::authorized_credentials] =
+                Json::arrayValue;
+            auto& arr(
+                jvParams[jss::deposit_preauth][jss::authorized_credentials]);
+
+            Json::Value jo;
+            jo[jss::credential_type] = strHex(std::string_view(credType));
+            arr.append(std::move(jo));
+
+            auto const jrr =
+                env.rpc("json", "ledger_entry", to_string(jvParams));
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
+        }
+
         {
             // Failed, issuer isn't string
             Json::Value jvParams;
@@ -1285,6 +1343,30 @@ class LedgerRPC_test : public beast::unit_test::suite
                 jrr[jss::result], "malformedAuthorizedCredentials", "");
         }
 
+        {
+            // Failed, issuer is an array
+            Json::Value jvParams;
+            jvParams[jss::ledger_index] = jss::validated;
+            jvParams[jss::deposit_preauth][jss::owner] = bob.human();
+
+            jvParams[jss::deposit_preauth][jss::authorized_credentials] =
+                Json::arrayValue;
+            auto& arr(
+                jvParams[jss::deposit_preauth][jss::authorized_credentials]);
+
+            Json::Value jo;
+            Json::Value payload = Json::arrayValue;
+            payload.append(42);
+            jo[jss::issuer] = std::move(payload);
+            jo[jss::credential_type] = strHex(std::string_view(credType));
+            arr.append(std::move(jo));
+
+            auto const jrr =
+                env.rpc("json", "ledger_entry", to_string(jvParams));
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
+        }
+
         {
             // Failed, issuer isn't valid encoded account
             Json::Value jvParams;
@@ -1307,12 +1389,32 @@ class LedgerRPC_test : public beast::unit_test::suite
                 jrr[jss::result], "malformedAuthorizedCredentials", "");
         }
 
+        {
+            // Failed, credential_type is not set
+            Json::Value jvParams;
+            jvParams[jss::ledger_index] = jss::validated;
+            jvParams[jss::deposit_preauth][jss::owner] = bob.human();
+
+            jvParams[jss::deposit_preauth][jss::authorized_credentials] =
+                Json::arrayValue;
+            auto& arr(
+                jvParams[jss::deposit_preauth][jss::authorized_credentials]);
+
+            Json::Value jo;
+            jo[jss::issuer] = issuer.human();
+            arr.append(std::move(jo));
+
+            auto const jrr =
+                env.rpc("json", "ledger_entry", to_string(jvParams));
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
+        }
+
         {
             // Failed, credential_type isn't string
             Json::Value jvParams;
             jvParams[jss::ledger_index] = jss::validated;
             jvParams[jss::deposit_preauth][jss::owner] = bob.human();
-            jvParams[jss::deposit_preauth][jss::authorized] = alice.human();
 
             jvParams[jss::deposit_preauth][jss::authorized_credentials] =
                 Json::arrayValue;
@@ -1326,15 +1428,39 @@ class LedgerRPC_test : public beast::unit_test::suite
 
             auto const jrr =
                 env.rpc("json", "ledger_entry", to_string(jvParams));
-            checkErrorValue(jrr[jss::result], "malformedRequest", "");
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
+        }
+
+        {
+            // Failed, credential_type is an array
+            Json::Value jvParams;
+            jvParams[jss::ledger_index] = jss::validated;
+            jvParams[jss::deposit_preauth][jss::owner] = bob.human();
+
+            jvParams[jss::deposit_preauth][jss::authorized_credentials] =
+                Json::arrayValue;
+            auto& arr(
+                jvParams[jss::deposit_preauth][jss::authorized_credentials]);
+
+            Json::Value jo;
+            jo[jss::issuer] = issuer.human();
+            Json::Value payload = Json::arrayValue;
+            payload.append(42);
+            jo[jss::credential_type] = std::move(payload);
+            arr.append(std::move(jo));
+
+            auto const jrr =
+                env.rpc("json", "ledger_entry", to_string(jvParams));
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
         }
 
         {
             // Failed, credential_type isn't hex encoded
             Json::Value jvParams;
             jvParams[jss::ledger_index] = jss::validated;
             jvParams[jss::deposit_preauth][jss::owner] = bob.human();
-            jvParams[jss::deposit_preauth][jss::authorized] = alice.human();
 
             jvParams[jss::deposit_preauth][jss::authorized_credentials] =
                 Json::arrayValue;
@@ -1348,7 +1474,8 @@ class LedgerRPC_test : public beast::unit_test::suite
 
             auto const jrr =
                 env.rpc("json", "ledger_entry", to_string(jvParams));
-            checkErrorValue(jrr[jss::result], "malformedRequest", "");
+            checkErrorValue(
+                jrr[jss::result], "malformedAuthorizedCredentials", "");
         }
     }
 
```

### src/xrpld/rpc/handlers/LedgerEntry.cpp
```diff
@@ -41,6 +41,12 @@ parseAuthorizeCredentials(Json::Value const& jv)
     STArray arr(sfAuthorizeCredentials, jv.size());
     for (auto const& jo : jv)
     {
+        if (!jo.isObject() ||  //
+            !jo.isMember(jss::issuer) || !jo[jss::issuer].isString() ||
+            !jo.isMember(jss::credential_type) ||
+            !jo[jss::credential_type].isString())
+            return {};
+
         auto const issuer = parseBase58<AccountID>(jo[jss::issuer].asString());
         if (!issuer || !*issuer)
             return {};
```
