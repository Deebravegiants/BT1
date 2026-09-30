# [?] Fix zcash-cli crash when printing help message

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2023-04-15
Source: https://github.com/zcash/zcash/commit/14c11c385a5dc2ebce407b8dcbc96c8c3ddd88ca
Type: security-commit

## Details
Fix zcash-cli crash when printing help message

When a `zcash-cli` command fails, it attempts to print the help message for the command. However,
making the `help` call can also fail, and there was a bug in this check, so that we tried to display
the help message when the `help` call failed, and tried to display the error when the `help` call
succeeded – both leading to an assertion failure.

This also makes some minor changes to the output formatting.

Fixes #6561

## Patch
### src/bitcoin-cli.cpp
```diff
@@ -212,12 +212,12 @@ UniValue ConvertValues(const std::string &strMethod, const std::vector<std::stri
                             auto helpMsg = CallRPC("help", ConvertValues("help", {strMethod}));
                             return "\n\n"
                                 + (helpMsg.has_value()
-                                   ? strprintf(
+                                   ? "Usage: " + helpMsg.value().get_str()
+                                   : strprintf(
                                            "An error occurred while attempting to retrieve the "
                                            "help text for %s: %s",
                                            strMethod,
-                                           helpMsg.error().get_str())
-                                   : helpMsg->get_str());
+                                           helpMsg.error().get_str()));
                         }
                     }));
         })
```

### src/rpc/client.cpp
```diff
@@ -189,7 +189,7 @@ std::string FormatConversionFailure(const std::string& strMethod, const Conversi
                         err.providedParams);
             },
             [](const UnparseableParam& err) {
-                return std::string("Error parsing JSON:") + err.unparsedParam;
+                return std::string("Error parsing JSON: ") + err.unparsedParam;
             }
         });
 }
```

### src/test/rpc_tests.cpp
```diff
@@ -404,7 +404,7 @@ BOOST_AUTO_TEST_CASE(rpc_insightexplorer)
     CheckRPCThrows("getblockhashes 1477641360 1477641360 {\"noOrphans\":true,\"logicalTimes\":1}",
         "JSON value is not a boolean as expected");
     CheckRPCThrows("getblockhashes 1477641360 1477641360 {\"noOrphans\":True,\"logicalTimes\":false}",
-        "Error parsing JSON:{\"noOrphans\":True,\"logicalTimes\":false}");
+        "Error parsing JSON: {\"noOrphans\":True,\"logicalTimes\":false}");
 
     // revert
     fExperimentalInsightExplorer = false;
```

### src/wallet/test/rpc_wallet_tests.cpp
```diff
@@ -1570,19 +1570,19 @@ BOOST_AUTO_TEST_CASE(rpc_z_mergetoaddress_parameters)
 
     // bad from address
     CheckRPCThrows("z_mergetoaddress ** " + taddr2,
-        "Error parsing JSON:**");
+        "Error parsing JSON: **");
 
     // bad from address
     CheckRPCThrows("z_mergetoaddress [\"**\"] " + taddr2,
         "Unknown address format: **");
 
     // bad from address
     CheckRPCThrows("z_mergetoaddress " + taddr1 + " " + taddr2,
-        "Error parsing JSON:" + taddr1);
+        "Error parsing JSON: " + taddr1);
 
     // bad from address
     CheckRPCThrows("z_mergetoaddress [" + taddr1 + "] " + taddr2,
-        "Error parsing JSON:[" + taddr1 + "]");
+        "Error parsing JSON: [" + taddr1 + "]");
 
     // bad to address
     CheckRPCThrows("z_mergetoaddress [\"" + taddr1 + "\"] INVALID" + taddr2,
```
