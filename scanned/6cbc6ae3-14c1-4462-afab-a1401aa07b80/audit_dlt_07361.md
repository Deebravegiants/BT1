# [?] Fix crash when stream closed without producing an element [DPP-853] (#12363)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-01-12
Source: https://github.com/digital-asset/daml/commit/a90122ef062e0de8eef8dbe9d8c1e7839512f86b
Type: security-commit

## Details
Fix crash when stream closed without producing an element [DPP-853] (#12363)

* Fix crash when stream closed without producing an element

CHANGELOG_BEGIN
CHANGELOG_END

* address review comments

## Patch
### ledger/participant-integration-api/src/main/scala/platform/apiserver/services/admin/SynchronousResponse.scala
```diff
@@ -55,13 +55,27 @@ class SynchronousResponse[Input, Entry, AcceptedEntry](
             }
             .completionTimeout(FiniteDuration(timeToLive.toMillis, TimeUnit.MILLISECONDS))
             .runWith(Sink.head)
-            .recoverWith { case _: TimeoutException =>
-              Future.failed(
-                errorFactories
-                  .isTimeoutUnknown_wasAborted("Request timed out", definiteAnswer = Some(false))(
-                    new DamlContextualizedErrorLogger(logger, loggingContext, Some(submissionId))
+            .recoverWith {
+              case _: TimeoutException =>
+                Future.failed(
+                  errorFactories
+                    .isTimeoutUnknown_wasAborted("Request timed out", definiteAnswer = Some(false))(
+                      new DamlContextualizedErrorLogger(logger, loggingContext, Some(submissionId))
+                    )
+                )
+              case _: NoSuchElementException =>
+                Future.failed(
+                  errorFactories.grpcError(
+                    errorFactories.SubmissionQueueErrors
+                      .queueClosed("Party submission")(
+                        new DamlContextualizedErrorLogger(
+                          logger,
+                          loggingContext,
+                          Some(submissionId),
+                        )
+                      )
                   )
-              )
+                )
             }
             .flatten
         case r: SubmissionResult.SynchronousError =>
```
