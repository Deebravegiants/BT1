# [?] Avoid race condition by creating unique version of verifier for each usage

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2020-01-20
Source: https://github.com/ergoplatform/ergo/commit/cb46911a17382c121a70eae46182919ad0235e26
Type: security-commit

## Details
Avoid race condition by creating unique version of verifier for each usage

## Patch
### src/test/scala/org/ergoplatform/utils/ErgoTestConstants.scala
```diff
@@ -78,7 +78,7 @@ trait ErgoTestConstants extends ScorexLogging {
   val emptyExtension: ExtensionCandidate = ExtensionCandidate(Seq())
   val emptyDataInputs: IndexedSeq[DataInput] = IndexedSeq()
   val emptyDataBoxes: IndexedSeq[ErgoBox] = IndexedSeq()
-  lazy val emptyVerifier: ErgoInterpreter = ErgoInterpreter(emptyStateContext.currentParameters)
+  def emptyVerifier: ErgoInterpreter = ErgoInterpreter(emptyStateContext.currentParameters)
 
   val defaultTimeout: Timeout = Timeout(14.seconds)
   val defaultAwaitDuration: FiniteDuration = defaultTimeout.duration + 1.second
```
