# [?] Fix security issue in BridgeStorageProvider

## Summary
Severity: Unknown
Chain: Rootstock
Component: rsksmart/rskj
Published: 2023-10-10
Source: https://github.com/rsksmart/rskj/commit/6d4749dcde26e6d98bb23c7f4cd3580f2d105b2b
Type: security-commit

## Details
Fix security issue in BridgeStorageProvider

## Patch
### rskj-core/src/main/java/co/rsk/peg/BridgeStorageProvider.java
```diff
@@ -1046,7 +1046,10 @@ private Federation deserializeFederationAccordingToVersion(
                     networkParameters
                 );
             default:
-                throw new IllegalArgumentException("Unknown Federation version: " + version);
+                return BridgeSerializationUtils.deserializeStandardMultisigFederation(
+                    data,
+                    networkParameters
+                );
         }
     }
 
```
