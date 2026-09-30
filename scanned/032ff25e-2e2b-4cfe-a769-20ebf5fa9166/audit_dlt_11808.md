# [?] fix: reconnect race condition (#3643)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/wagmi
Published: 2024-03-17
Source: https://github.com/wevm/wagmi/commit/e46bcd4738a18da15b53f6612b614379c1985374
Type: security-commit

## Details
fix: reconnect race condition (#3643)

* fix: reconnect race condition

* Create quick-hairs-nail.md

---------

Co-authored-by: jxom <jakemoxey@gmail.com>

## Patch
### .changeset/quick-hairs-nail.md
```diff
@@ -0,0 +1,6 @@
+---
+"@wagmi/core": patch
+"wagmi": patch
+---
+
+Fixed race condition arising from `reconnect`.
```

### packages/core/src/actions/reconnect.test.ts
```diff
@@ -68,3 +68,11 @@ test("behavior: doesn't reconnect if already reconnecting", async () => {
   ).resolves.toStrictEqual([])
   config.setState((x) => ({ ...x, status: previousStatus }))
 })
+
+test("behaviour: doesn't overwrite connected status", async () => {
+  config.setState((x) => ({ ...x, status: 'connected' }))
+  await expect(
+    reconnect(config, { connectors: [connector] }),
+  ).resolves.toStrictEqual([])
+  expect(config.state.status).toEqual('connected')
+})
```

### packages/core/src/actions/reconnect.ts
```diff
@@ -106,15 +106,21 @@ export async function reconnect(
     connected = true
   }
 
-  // If connecting didn't succeed, set to disconnected
-  if (!connected)
-    config.setState((x) => ({
-      ...x,
-      connections: new Map(),
-      current: undefined,
-      status: 'disconnected',
-    }))
-  else config.setState((x) => ({ ...x, status: 'connected' }))
+  // Prevent overwriting connected status from race condition
+  if (
+    config.state.status === 'reconnecting' ||
+    config.state.status === 'connecting'
+  ) {
+    // If connecting didn't succeed, set to disconnected
+    if (!connected)
+      config.setState((x) => ({
+        ...x,
+        connections: new Map(),
+        current: undefined,
+        status: 'disconnected',
+      }))
+    else config.setState((x) => ({ ...x, status: 'connected' }))
+  }
 
   isReconnecting = false
   return connections
```
