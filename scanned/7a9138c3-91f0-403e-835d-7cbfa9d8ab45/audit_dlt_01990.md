# [?] CORDA-3932 Correct race condition in FlowVersioningTest (#6536)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2020-07-31
Source: https://github.com/corda/corda/commit/68feb1c35fa37379f492803fb3bf047321883d4d
Type: security-commit

## Details
CORDA-3932 Correct race condition in FlowVersioningTest (#6536)

Correct race condition in FlowVersioningTest where the last message is read (and the session close can be triggered)
before one side has finished reading metadata from the session.

## Patch
### node/src/integration-test/kotlin/net/corda/node/services/statemachine/FlowVersioningTest.kt
```diff
@@ -33,13 +33,19 @@ class FlowVersioningTest : NodeBasedTest() {
     private class PretendInitiatingCoreFlow(val initiatedParty: Party) : FlowLogic<Pair<Int, Int>>() {
         @Suspendable
         override fun call(): Pair<Int, Int> {
-            // Execute receive() outside of the Pair constructor to avoid Kotlin/Quasar instrumentation bug.
             val session = initiateFlow(initiatedParty)
-            val alicePlatformVersionAccordingToBob = session.receive<Int>().unwrap { it }
-            return Pair(
-                    alicePlatformVersionAccordingToBob,
-                    session.getCounterpartyFlowInfo().flowVersion
-            )
+            return try {
+                // Get counterparty flow info before we receive Alice's data, to ensure the flow is still open
+                val bobPlatformVersionAccordingToAlice = session.getCounterpartyFlowInfo().flowVersion
+                // Execute receive() outside of the Pair constructor to avoid Kotlin/Quasar instrumentation bug.
+                val alicePlatformVersionAccordingToBob = session.receive<Int>().unwrap { it }
+                Pair(
+                        alicePlatformVersionAccordingToBob,
+                        bobPlatformVersionAccordingToAlice
+                )
+            } finally {
+                session.close()
+            }
         }
     }
 
```
