# [?] Use FlowTimeOut exception rather than SQL deadlock in unit tests to avoid hitting the exponential back-off. (#4527)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2019-01-10
Source: https://github.com/corda/corda/commit/b5fc095288f5afa37fa167a810db88be62bdec18
Type: security-commit

## Details
Use FlowTimeOut exception rather than SQL deadlock in unit tests to avoid hitting the exponential back-off. (#4527)

## Patch
### .idea/compiler.xml
```diff
@@ -44,6 +44,8 @@
       <module name="corda-core_integrationTest" target="1.8" />
       <module name="corda-core_smokeTest" target="1.8" />
       <module name="corda-finance_integrationTest" target="1.8" />
+      <module name="corda-isolated_main" target="1.8" />
+      <module name="corda-isolated_test" target="1.8" />
       <module name="corda-project_buildSrc_main" target="1.8" />
       <module name="corda-project_buildSrc_test" target="1.8" />
       <module name="corda-project_canonicalizer_main" target="1.8" />
```

### node/src/integration-test/kotlin/net/corda/node/flows/FlowRetryTest.kt
```diff
@@ -16,6 +16,7 @@ import net.corda.core.utilities.ProgressTracker
 import net.corda.core.utilities.getOrThrow
 import net.corda.core.utilities.unwrap
 import net.corda.node.services.Permissions
+import net.corda.node.services.statemachine.FlowTimeoutException
 import net.corda.testing.core.ALICE_NAME
 import net.corda.testing.core.BOB_NAME
 import net.corda.testing.core.singleIdentity
@@ -117,8 +118,6 @@ fun isQuasarAgentSpecified(): Boolean {
     return jvmArgs.any { it.startsWith("-javaagent:") && it.contains("quasar") }
 }
 
-class ExceptionToCauseRetry : SQLException("deadlock")
-
 class ExceptionToCauseFiniteRetry : ConstraintViolationException("Faked violation", SQLException("Fake"), "Fake name")
 
 @StartableByRPC
@@ -135,7 +134,7 @@ class InitiatorFlow(private val sessionsCount: Int, private val iterationsCount:
             val visited = Visited(sessionNum, iterationNum, step)
             if (visited !in seen) {
                 seen += visited
-                throw ExceptionToCauseRetry()
+                throw FlowTimeoutException()
             }
         }
     }
@@ -186,7 +185,7 @@ class InitiatedFlow(val session: FlowSession) : FlowLogic<Any>() {
             val visited = Visited(sessionNum, iterationNum, step)
             if (visited !in seen) {
                 seen += visited
-                throw ExceptionToCauseRetry()
+                throw FlowTimeoutException()
             }
         }
     }
```
