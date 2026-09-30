# [?] cosmos-sdk patched version to a vulnerability (#1247)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/heimdall
Published: 2025-02-21
Source: https://github.com/0xPolygon/heimdall/commit/4a91c99f13f36154e3d7f0b87af1cff0af118200
Type: security-commit

## Details
cosmos-sdk patched version to a vulnerability (#1247)

## Patch
### go.mod
```diff
@@ -5,7 +5,7 @@ go 1.23.6
 require (
 	github.com/RichardKnop/machinery v1.10.6
 	github.com/cbergoon/merkletree v0.2.0
-	github.com/cosmos/cosmos-sdk v0.50.6
+	github.com/cosmos/cosmos-sdk v0.50.12
 	github.com/ethereum/go-ethereum v1.14.13
 	github.com/go-kit/log v0.2.1
 	github.com/gogo/protobuf v1.3.2
```
