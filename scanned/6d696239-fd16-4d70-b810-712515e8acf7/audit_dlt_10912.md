# [?] Fix BigDecimal to Long overflow checking.

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2018-04-20
Source: https://github.com/wavesplatform/Waves/commit/168548352cca86e659d3ecacd607d40eefeb5f5f
Type: security-commit

## Details
Fix BigDecimal to Long overflow checking.

## Patch
### src/main/scala/com/wavesplatform/state2/Diff.scala
```diff
@@ -96,8 +96,13 @@ object Sponsorship {
       .map(_ + fs.sponsoredFeesDelay)
       .getOrElse(Int.MaxValue)
 
-  def toWaves(assetFee: Long, sponsorship: Long): Long =
-    (BigDecimal(assetFee) * BigDecimal(Sponsorship.FeeUnit) / BigDecimal(sponsorship)).toLongExact
+  def toWaves(assetFee: Long, sponsorship: Long): Long = {
+    val waves = (BigDecimal(assetFee) * BigDecimal(Sponsorship.FeeUnit)) / BigDecimal(sponsorship)
+    if (waves > Long.MaxValue) {
+      throw new java.lang.ArithmeticException("Overflow")
+    }
+    waves.toLong
+  }
 }
 
 case class Diff(transactions: Map[ByteStr, (Int, Transaction, Set[Address])],
```
