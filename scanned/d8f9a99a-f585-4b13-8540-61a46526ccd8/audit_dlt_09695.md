# [?] stack overflow fix for json serialization

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2020-11-08
Source: https://github.com/ergoplatform/ergo/commit/2fd49da4e616255f5f2d6b3dfa824b36212babe0
Type: security-commit

## Details
stack overflow fix for json serialization

## Patch
### src/main/scala/org/ergoplatform/http/api/ApiCodecs.scala
```diff
@@ -52,8 +52,6 @@ trait ApiCodecs extends JsonCodecs {
 
   implicit val proveDlogEncoder: Encoder[ProveDlog] = _.pkBytes.asJson
 
-  implicit val encodedTokenIdEncoder: Encoder[EncodedTokenId] = _.asJson
-
   implicit val balancesSnapshotEncoder: Encoder[WalletDigest] = { v =>
     import v._
     Json.obj(
```
