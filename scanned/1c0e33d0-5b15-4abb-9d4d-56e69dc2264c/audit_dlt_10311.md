# [?] Add comment in fixed security issue

## Summary
Severity: Unknown
Chain: Rootstock
Component: rsksmart/rskj
Published: 2023-10-10
Source: https://github.com/rsksmart/rskj/commit/edeeedd6af7ca4af0e3c7213e2da53f84035a885
Type: security-commit

## Details
Add comment in fixed security issue

## Patch
### rskj-core/src/main/java/co/rsk/peg/BridgeStorageProvider.java
```diff
@@ -1046,6 +1046,7 @@ private Federation deserializeFederationAccordingToVersion(
                     networkParameters
                 );
             default:
+                // To keep backwards compatibility
                 return BridgeSerializationUtils.deserializeStandardMultisigFederation(
                     data,
                     networkParameters
```
