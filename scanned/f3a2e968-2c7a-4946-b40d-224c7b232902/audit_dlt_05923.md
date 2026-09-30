# [?] Fix data race in workflow engine beholder test polling (#22927)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-06-24
Source: https://github.com/smartcontractkit/chainlink/commit/bcb30d320b282adb7a0ecb8a723a41a049e65273
Type: security-commit

## Details
Fix data race in workflow engine beholder test polling (#22927)

Fix data race in workflow engine beholder test polling.

Filter beholdertest.Messages by beholder_entity so reads take the RLock
path while the engine emits user logs and base messages concurrently.

## Patch
### core/services/workflows/v2/engine_test.go
```diff
@@ -2442,6 +2442,20 @@ type observedBaseMessage struct {
 	Labels map[string]string
 }
 
+// beholdertest.Messages(t) returns the internal slice without locking, which races with
+// concurrent Emit under -race. Filter by beholder_entity so Messages uses the RLock path.
+const beholderEntityBaseMessage = "BaseMessage"
+
+func beholderBaseMessages(t *testing.T, observer beholdertest.Observer) []beholder.Message {
+	t.Helper()
+	return observer.Messages(t, "beholder_entity", beholderEntityBaseMessage)
+}
+
+func beholderUserLogMessages(t *testing.T, observer beholdertest.Observer) []beholder.Message {
+	t.Helper()
+	return observer.Messages(t, "beholder_entity", fmt.Sprintf("%s.%s", workflowEvents.ProtoPkg, workflowEvents.UserLogs))
+}
+
 // eventLabelsMatchStatus returns observed BaseMessages and the label set still being
 // searched for. missing is nil when a message with all expected labels is found.
 func eventLabelsMatchStatus(msgs []beholder.Message, want map[string]string) (observed []observedBaseMessage, missing map[string]string) {
@@ -2483,7 +2497,7 @@ func requireEventsLabels(t *testing.T, beholderObserver beholdertest.Observer, w
 	}
 
 	require.EventuallyWithT(t, func(c *assert.CollectT) {
-		observed, missing := eventLabelsMatchStatus(beholderObserver.Messages(t), want)
+		observed, missing := eventLabelsMatchStatus(beholderBaseMessages(t, beholderObserver), want)
 		if missing != nil {
 			assert.Fail(c, fmt.Sprintf(
 				"event labels not found\n  expected labels: %v\n  observed base messages (%d):\n%s",
@@ -2532,7 +2546,7 @@ func requireEventsMessages(t *testing.T, beholderObserver beholdertest.Observer,
 	}
 
 	require.EventuallyWithT(t, func(c *assert.CollectT) {
-		observed, missing := eventMessagesMatchStatus(beholderObserver.Messages(t), expected)
+		observed, missing := eventMessagesMatchStatus(beholderBaseMessages(t, beholderObserver), expected)
 		if len(missing) > 0 {
 			found := expected[:len(expected)-len(missing)]
 			assert.Fail(c, fmt.Sprintf(
@@ -2579,7 +2593,7 @@ func requireUserLogs(t *testing.T, beholderObserver beholdertest.Observer, expec
 
 	require.EventuallyWithT(t, func(c *assert.CollectT) {
 		observed, missing := userLogMatchStatus(
-			beholderObserver.Messages(t),
+			beholderUserLogMessages(t, beholderObserver),
 			expectedSubstrings,
 		)
 		if len(missing) > 0 {
```
