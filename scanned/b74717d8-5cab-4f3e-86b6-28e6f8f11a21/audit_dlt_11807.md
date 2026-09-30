# [?] Fix race condition in injected.ts (#4207)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/wagmi
Published: 2024-09-27
Source: https://github.com/wevm/wagmi/commit/56f2482508f2ba71bd6b0295c70c6abca7101e57
Type: security-commit

## Details
Fix race condition in injected.ts (#4207)

* Fix race condition in injected.ts

It can hangs if "once" catches an event with unexpected chainId

* chore: tweaks

---------

Co-authored-by: Tom Meagher <tom@meagher.co>

## Patch
### .changeset/hungry-colts-flow.md
```diff
@@ -0,0 +1,6 @@
+---
+"@wagmi/connectors": patch
+"@wagmi/core": patch
+---
+
+Updated chain switch listener for `injected` and `metaMask` to be more robust.
```

### packages/connectors/src/metaMask.ts
```diff
@@ -239,11 +239,15 @@ export function metaMask(parameters: MetaMaskParameters = {}) {
               if (currentChainId === chainId)
                 config.emitter.emit('change', { chainId })
             }),
-          new Promise<void>((resolve) =>
-            config.emitter.once('change', ({ chainId: currentChainId }) => {
-              if (currentChainId === chainId) resolve()
-            }),
-          ),
+          new Promise<void>((resolve) => {
+            const listener = ((data) => {
+              if ('chainId' in data && data.chainId === chainId) {
+                config.emitter.off('change', listener)
+                resolve()
+              }
+            }) satisfies Parameters<typeof config.emitter.on>[1]
+            config.emitter.on('change', listener)
+          }),
         ])
         return chain
       } catch (err) {
```

### packages/core/src/connectors/injected.ts
```diff
@@ -428,11 +428,15 @@ export function injected(parameters: InjectedParameters = {}) {
               if (currentChainId === chainId)
                 config.emitter.emit('change', { chainId })
             }),
-          new Promise<void>((resolve) =>
-            config.emitter.once('change', ({ chainId: currentChainId }) => {
-              if (currentChainId === chainId) resolve()
-            }),
-          ),
+          new Promise<void>((resolve) => {
+            const listener = ((data) => {
+              if ('chainId' in data && data.chainId === chainId) {
+                config.emitter.off('change', listener)
+                resolve()
+              }
+            }) satisfies Parameters<typeof config.emitter.on>[1]
+            config.emitter.on('change', listener)
+          }),
         ])
         return chain
       } catch (err) {
```
