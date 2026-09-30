# [?] Fix race condition in unit test websocket.bootstrap (#3365)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-07-03
Source: https://github.com/nanocurrency/nano-node/commit/f27162531ef5e9426e50afddf6711420e1dd225e
Type: security-commit

## Details
Fix race condition in unit test websocket.bootstrap (#3365)

## Patch
### nano/core_test/websocket.cpp
```diff
@@ -724,7 +724,7 @@ TEST (websocket, bootstrap)
 
 	// Start bootstrap attempt
 	node1->bootstrap_initiator.bootstrap (true, "123abc");
-	ASSERT_NE (nullptr, node1->bootstrap_initiator.current_attempt ());
+	ASSERT_TIMELY (5s, nullptr == node1->bootstrap_initiator.current_attempt ());
 
 	// Wait for the bootstrap notification
 	ASSERT_TIMELY (5s, future.wait_for (0s) == std::future_status::ready);
```
