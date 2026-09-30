# [?] Fix existing race condition

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2026-04-12
Source: https://github.com/NomicFoundation/hardhat/commit/a405dc4fed53e3d4e42ea1c39ce6892807f8ad10
Type: security-commit

## Details
Fix existing race condition

## Patch
### packages/hardhat/src/internal/builtin-plugins/solidity-test/runner.ts
```diff
@@ -31,7 +31,7 @@ import { formatArtifactId } from "./formatters.js";
  * Despite the changes, the signature of the function should still be considered
  * a draft that may change in the future.
  *
- * TODO: Once the signature is finalized, give feedback to the EDR team.
+ * Important TODO: Transform this into an AsyncGenerator<SuiteResult, SolidityTestResult, void>
  */
 export function run(
   chainType: ChainType,
@@ -41,67 +41,75 @@ export function run(
   tracingConfig: TracingConfigWithBuffers,
   sourceNameToUserSourceName: Map<string, string>,
 ): TestsStream {
-  const stream = new ReadableStream<TestEvent>({
-    async start(controller) {
-      if (testSuiteIds.length === 0) {
-        controller.close();
-        return;
-      }
-      let runCompleted = false;
+  const stream = new Readable({
+    objectMode: true,
+    read() {},
+  });
 
-      const remainingSuites = new Set(
-        testSuiteIds.map((id) =>
-          formatArtifactId(id, sourceNameToUserSourceName),
-        ),
-      );
+  if (testSuiteIds.length === 0) {
+    stream.push(null);
+    return stream;
+  }
 
-      // TODO: Add support for predeploys once EDR supports them.
-      try {
-        const edrContext = await getGlobalEdrContext();
-        const solidityTestResult = await edrContext.runSolidityTests(
-          hardhatChainTypeToEdrChainType(chainType),
-          artifacts,
-          testSuiteIds,
-          testRunnerConfig,
-          tracingConfig,
-          (suiteResult) => {
-            controller.enqueue({
-              type: "suite:done",
-              data: suiteResult,
-            });
-            remainingSuites.delete(
-              formatArtifactId(suiteResult.id, sourceNameToUserSourceName),
-            );
-            if (remainingSuites.size === 0) {
-              if (runCompleted) {
-                controller.close();
-              }
-            }
-          },
-        );
-        controller.enqueue({
-          type: "run:done",
-          data: solidityTestResult,
-        });
-        runCompleted = true;
+  let runCompleted = false;
+
+  const remainingSuites = new Set(
+    testSuiteIds.map((id) => formatArtifactId(id, sourceNameToUserSourceName)),
+  );
 
-        if (remainingSuites.size === 0) {
-          controller.close();
-        }
-      } catch (error) {
-        ensureError(error);
+  // Start the async work immediately. The read() callback is a no-op
+  // because we push data proactively from the EDR suite-completion
+  // callback. Using a native Readable (instead of a web ReadableStream
+  // wrapped with Readable.from) avoids a race where Node.js stream
+  // cleanup cancels the web reader while the async start callback still
+  // has pending work — push() on a destroyed Readable is a safe no-op.
+  // TODO: Add support for predeploys once EDR supports them.
+  void (async () => {
+    try {
+      const edrContext = await getGlobalEdrContext();
+      const solidityTestResult = await edrContext.runSolidityTests(
+        hardhatChainTypeToEdrChainType(chainType),
+        artifacts,
+        testSuiteIds,
+        testRunnerConfig,
+        tracingConfig,
+        (suiteResult) => {
+          stream.push({
+            type: "suite:done",
+            data: suiteResult,
+          } satisfies TestEvent);
+          remainingSuites.delete(
+            formatArtifactId(suiteResult.id, sourceNameToUserSourceName),
+          );
+          if (remainingSuites.size === 0) {
+            if (runCompleted) {
+              stream.push(null);
+            }
+          }
+        },
+      );
+      stream.push({
+        type: "run:done",
+        data: solidityTestResult,
+      } satisfies TestEvent);
+      runCompleted = true;
 
-        controller.error(
-          new HardhatError(
-            HardhatError.ERRORS.CORE.SOLIDITY_TESTS.UNHANDLED_EDR_ERROR_SOLIDITY_TESTS,
-            {
-              error: error.message,
-            },
-          ),
-        );
+      if (remainingSuites.size === 0) {
+        stream.push(null);
       }
-    },
-  });
+    } catch (error) {
+      ensureError(error);
+
+      stream.destroy(
+        new HardhatError(
+          HardhatError.ERRORS.CORE.SOLIDITY_TESTS.UNHANDLED_EDR_ERROR_SOLIDITY_TESTS,
+          {
+            error: error.message,
+          },
+        ),
+      );
+    }
+  })();
 
-  return Readable.from(stream);
+  return stream;
 }
```
