# [?] docs: add a comment on signature malleability

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-07-31
Source: https://github.com/morpho-org/morpho-blue/commit/a901b95fa4ffeb4dd32b6776500dca255417d557
Type: security-commit

## Details
docs: add a comment on signature malleability

## Patch
### src/Blue.sol
```diff
@@ -299,6 +299,7 @@ contract Blue is IFlashLender {
 
     // Authorizations.
 
+    /// @dev The signature is malleable, but it has no impact on the security here.
     function setAuthorization(
         address authorizer,
         address authorizee,
```
