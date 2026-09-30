# [?] i1702 fixing non-deterministic test failure

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2022-05-14
Source: https://github.com/ergoplatform/ergo/commit/ff9eb55b606f9a9057ecb43d4cb88f136ed05389
Type: security-commit

## Details
i1702 fixing non-deterministic test failure

## Patch
### src/test/scala/org/ergoplatform/network/ErgoNodeViewSynchronizerSpecification.scala
```diff
@@ -94,7 +94,7 @@ class ErgoNodeViewSynchronizerSpecification extends HistoryTestHelpers with Matc
     }
   }
 
-  override implicit val patienceConfig: PatienceConfig = PatienceConfig(5.seconds, 100.millis)
+  override implicit val patienceConfig: PatienceConfig = PatienceConfig(10.seconds, 100.millis)
   val history = generateHistory(verifyTransactions = true, StateType.Utxo, PoPoWBootstrap = false, blocksToKeep = -1)
   val olderChain = genHeaderChain(2010, history, diffBitsOpt = None, useRealTs = false)
   val chain = olderChain.take(2000)
```
