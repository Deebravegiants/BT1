# [?] NODE-1455: Fix overflow test

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2019-02-06
Source: https://github.com/wavesplatform/Waves/commit/69651c7cbd6f8e5eeb20bd99cfda60cad10cb7fe
Type: security-commit

## Details
NODE-1455: Fix overflow test

## Patch
### src/test/scala/com/wavesplatform/http/AssetsBroadcastRouteSpec.scala
```diff
@@ -144,8 +144,16 @@ class AssetsBroadcastRouteSpec extends RouteSpec("/assets/broadcast/") with Requ
         forAll(longAttachment) { a =>
           posting(tr.copy(attachment = Some(a))) should produce(CustomValidationError("invalid.attachment"))
         }
-        forAll(posNum[Long]) { quantity =>
-          posting(tr.copy(amount = quantity, fee = Long.MaxValue)) should produce(OverflowError)
+        forAll(posNum[Long], assetIdGen) { (quantity, assetId) =>
+          val maybeAssetIdStr = assetId.map(_.base58)
+          posting(
+            tr.copy(
+              amount = quantity,
+              assetId = maybeAssetIdStr,
+              fee = Long.MaxValue,
+              feeAssetId = maybeAssetIdStr
+            )
+          ) should produce(OverflowError)
         }
         forAll(nonPositiveLong) { fee =>
           posting(tr.copy(fee = fee)) should produce(InsufficientFee())
```
