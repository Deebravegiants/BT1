# [?] CORDA-1892 CRaSH shell flow start fix for similar flow names. (#3874)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2018-09-11
Source: https://github.com/corda/corda/commit/37c7fff8b130a2d68c9910d688b7a2944518959b
Type: security-commit

## Details
CORDA-1892 CRaSH shell flow start fix for similar flow names. (#3874)

* Added fix and associated unit test.

* Fixed broken unit test + added another test case + used NoOpFlows + use Mock output object to assert correct result output.

* Remove unnecessary additional println.

* Minor cleanup in test code.

* Relax nameFragment matching to cater for fully qualified and simple Flow classname specifications.

* Remove superfluous check.

* Minor fix + added additional Unit Test cases to cover all scenarios.

* Reverted back to original behaviour + extra check to avoid ambiguity for exact match.

* Changes following final PR review comments.

## Patch
### tools/shell/src/integration-test/kotlin/net/corda/tools/shell/InteractiveShellIntegrationTest.kt
```diff
@@ -3,10 +3,16 @@ package net.corda.tools.shell
 import com.google.common.io.Files
 import com.jcraft.jsch.ChannelExec
 import com.jcraft.jsch.JSch
+import com.nhaarman.mockito_kotlin.any
+import com.nhaarman.mockito_kotlin.doAnswer
+import com.nhaarman.mockito_kotlin.mock
 import net.corda.client.rpc.RPCException
+import net.corda.core.flows.FlowLogic
+import net.corda.core.flows.StartableByRPC
 import net.corda.core.internal.div
 import net.corda.core.messaging.ClientRpcSslOptions
 import net.corda.core.messaging.CordaRPCOps
+import net.corda.core.utilities.ProgressTracker
 import net.corda.core.utilities.getOrThrow
 import net.corda.node.services.Permissions
 import net.corda.node.services.Permissions.Companion.all
@@ -21,10 +27,12 @@ import net.corda.testing.driver.driver
 import net.corda.testing.driver.internal.NodeHandleInternal
 import net.corda.testing.internal.useSslRpcOverrides
 import net.corda.testing.node.User
+import net.corda.tools.shell.utlities.ANSIProgressRenderer
 import org.apache.activemq.artemis.api.core.ActiveMQSecurityException
 import org.assertj.core.api.Assertions.assertThat
 import org.assertj.core.api.Assertions.assertThatThrownBy
 import org.bouncycastle.util.io.Streams
+import org.crsh.text.RenderPrintWriter
 import org.junit.Ignore
 import org.junit.Rule
 import org.junit.Test
@@ -236,4 +244,159 @@ class InteractiveShellIntegrationTest {
 
         }
     }
+
+    @Suppress("UNUSED")
+    @StartableByRPC
+    class NoOpFlow : FlowLogic<Unit>() {
+        override val progressTracker = ProgressTracker()
+        override fun call() {
+            println("NO OP!")
+        }
+    }
+
+    @Suppress("UNUSED")
+    @StartableByRPC
+    class NoOpFlowA : FlowLogic<Unit>() {
+        override val progressTracker = ProgressTracker()
+        override fun call() {
+            println("NO OP! (A)")
+        }
+    }
+
+    @Suppress("UNUSED")
+    @StartableByRPC
+    class BurbleFlow : FlowLogic<Unit>() {
+        override val progressTracker = ProgressTracker()
+        override fun call() {
+            println("NO OP! (Burble)")
+        }
+    }
+
+    @Test
+    fun `shell should start flow with fully qualified class name`() {
+        val user = User("u", "p", setOf(all()))
+        var successful = false
+        driver(DriverParameters(notarySpecs = emptyList())) {
+            val nodeFuture = startNode(providedName = ALICE_NAME, rpcUsers = listOf(user), startInSameProcess = true)
+            val node = nodeFuture.getOrThrow()
+
+            val conf = ShellConfiguration(commandsDirectory = Files.createTempDir().toPath(),
+                    user = user.username, password = user.password,
+                    hostAndPort = node.rpcAddress)
+            InteractiveShell.startShell(conf)
+
+            // setup and configure some mocks required by InteractiveShell.runFlowByNameFragment()
+            val output = mock<RenderPrintWriter> {
+                on { println(any<String>()) } doAnswer {
+                    val line = it.arguments[0]
+                    println("$line")
+                    if ((line is String) && (line.startsWith("Flow completed with result:")))
+                        successful = true
+                }
+            }
+            val ansiProgressRenderer = mock<ANSIProgressRenderer> {
+                on { render(any(), any()) }  doAnswer { InteractiveShell.latch.countDown() }
+            }
+            InteractiveShell.runFlowByNameFragment(
+                    InteractiveShellIntegrationTest::class.qualifiedName + "\$NoOpFlow",
+                    "", output, node.rpc, ansiProgressRenderer)
+        }
+        assertThat(successful).isTrue()
+    }
+
+    @Test
+    fun `shell should start flow with unique un-qualified class name`() {
+        val user = User("u", "p", setOf(all()))
+        var successful = false
+        driver(DriverParameters(notarySpecs = emptyList())) {
+            val nodeFuture = startNode(providedName = ALICE_NAME, rpcUsers = listOf(user), startInSameProcess = true)
+            val node = nodeFuture.getOrThrow()
+
+            val conf = ShellConfiguration(commandsDirectory = Files.createTempDir().toPath(),
+                    user = user.username, password = user.password,
+                    hostAndPort = node.rpcAddress)
+            InteractiveShell.startShell(conf)
+
+            // setup and configure some mocks required by InteractiveShell.runFlowByNameFragment()
+            val output = mock<RenderPrintWriter> {
+                on { println(any<String>()) } doAnswer {
+                    val line = it.arguments[0]
+                    println("$line")
+                    if ((line is String) && (line.startsWith("Flow completed with result:")))
+                        successful = true
+                }
+            }
+            val ansiProgressRenderer = mock<ANSIProgressRenderer> {
+                on { render(any(), any()) }  doAnswer { InteractiveShell.latch.countDown() }
+            }
+            InteractiveShell.runFlowByNameFragment(
+                    "InteractiveShellIntegrationTest\$NoOpFlowA",
+                    "", output, node.rpc, ansiProgressRenderer)
+        }
+        assertThat(successful).isTrue()
+    }
+
+    @Test
+    fun `shell should fail to start flow with ambiguous class name`() {
+        val user = User("u", "p", setOf(all()))
+        var successful = false
+        driver(DriverParameters(notarySpecs = emptyList())) {
+            val nodeFuture = startNode(providedName = ALICE_NAME, rpcUsers = listOf(user), startInSameProcess = true)
+            val node = nodeFuture.getOrThrow()
+
+            val conf = ShellConfiguration(commandsDirectory = Files.createTempDir().toPath(),
+                    user = user.username, password = user.password,
+                    hostAndPort = node.rpcAddress)
+            InteractiveShell.startShell(conf)
+
+            // setup and configure some mocks required by InteractiveShell.runFlowByNameFragment()
+            val output = mock<RenderPrintWriter> {
+                on { println(any<String>()) } doAnswer {
+                    val line = it.arguments[0]
+                    println("$line")
+                    if ((line is String) && (line.startsWith("Ambiguous name provided, please be more specific.")))
+                        successful = true
+                }
+            }
+            val ansiProgressRenderer = mock<ANSIProgressRenderer> {
+                on { render(any(), any()) }  doAnswer { InteractiveShell.latch.countDown() }
+            }
+            InteractiveShell.runFlowByNameFragment(
+                    InteractiveShellIntegrationTest::class.qualifiedName + "\$NoOpFlo",
+                    "", output, node.rpc, ansiProgressRenderer)
+        }
+        assertThat(successful).isTrue()
+    }
+
+    @Test
+    fun `shell should start flow with partially matching class name`() {
+        val user = User("u", "p", setOf(all()))
+        var successful = false
+        driver(DriverParameters(notarySpecs = emptyList())) {
+            val nodeFuture = startNode(providedName = ALICE_NAME, rpcUsers = listOf(user), startInSameProcess = true)
+            val node = nodeFuture.getOrThrow()
+
+            val conf = ShellConfiguration(commandsDirectory = Files.createTempDir().toPath(),
+                    user = user.username, password = user.password,
+                    hostAndPort = node.rpcAddress)
+            InteractiveShell.startShell(conf)
+
+            // setup and configure some mocks required by InteractiveShell.runFlowByNameFragment()
+            val output = mock<RenderPrintWriter> {
+                on { println(any<String>()) } doAnswer {
+                    val line = it.arguments[0]
+                    println("$line")
+                    if ((line is String) && (line.startsWith("Flow completed with result")))
+                        successful = true
+                }
+            }
+            val ansiProgressRenderer = mock<ANSIProgressRenderer> {
+                on { render(any(), any()) }  doAnswer { InteractiveShell.latch.countDown() }
+            }
+            InteractiveShell.runFlowByNameFragment(
+                    "Burble",
+                    "", output, node.rpc, ansiProgressRenderer)
+        }
+        assertThat(successful).isTrue()
+    }
 }
\ No newline at end of file
```

### tools/shell/src/main/kotlin/net/corda/tools/shell/InteractiveShell.kt
```diff
@@ -209,6 +209,10 @@ object InteractiveShell {
     // TODO: This should become the default renderer rather than something used specifically by commands.
     private val outputMapper by lazy { createOutputMapper() }
 
+    @VisibleForTesting
+    lateinit var latch: CountDownLatch
+        private set
+
     /**
      * Called from the 'flow' shell command. Takes a name fragment and finds a matching flow, or prints out
      * the list of options if the request is ambiguous. Then parses [inputData] as constructor arguments using
@@ -220,7 +224,7 @@ object InteractiveShell {
                               output: RenderPrintWriter,
                               rpcOps: CordaRPCOps,
                               ansiProgressRenderer: ANSIProgressRenderer,
-                              om: ObjectMapper) {
+                              om: ObjectMapper = outputMapper) {
         val matches = try {
             rpcOps.registeredFlows().filter { nameFragment in it }
         } catch (e: PermissionException) {
@@ -230,23 +234,24 @@ object InteractiveShell {
         if (matches.isEmpty()) {
             output.println("No matching flow found, run 'flow list' to see your options.", Color.red)
             return
-        } else if (matches.size > 1) {
+        } else if (matches.size > 1 && matches.find { it.endsWith(nameFragment)} == null) {
             output.println("Ambiguous name provided, please be more specific. Your options are:")
             matches.forEachIndexed { i, s -> output.println("${i + 1}. $s", Color.yellow) }
             return
         }
 
+        val flowName = matches.find { it.endsWith(nameFragment)} ?: matches.single()
         val flowClazz: Class<FlowLogic<*>> = if (classLoader != null) {
-            uncheckedCast(Class.forName(matches.single(), true, classLoader))
+            uncheckedCast(Class.forName(flowName, true, classLoader))
         } else {
-            uncheckedCast(Class.forName(matches.single()))
+            uncheckedCast(Class.forName(flowName))
         }
         try {
             // Show the progress tracker on the console until the flow completes or is interrupted with a
             // Ctrl-C keypress.
             val stateObservable = runFlowFromString({ clazz, args -> rpcOps.startTrackedFlowDynamic(clazz, *args) }, inputData, flowClazz, om)
 
-            val latch = CountDownLatch(1)
+            latch = CountDownLatch(1)
             ansiProgressRenderer.render(stateObservable, latch::countDown)
             // Wait for the flow to end and the progress tracker to notice. By the time the latch is released
             // the tracker is done with the screen.
```
