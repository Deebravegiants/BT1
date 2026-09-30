# [?] fix: Network controller race condition after state update (#5122)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2025-01-17
Source: https://github.com/MetaMask/core/commit/0106a5feb17cd460b1ed30aea15a7a25c72fdfee
Type: security-commit

## Details
fix: Network controller race condition after state update (#5122)

## Explanation

Fixes a race condition where:

- You update a network with a new endpoint.
- In the `stateChange` subscription callback, call
`getNetworkConfigurationByNetworkClientId` on the new endpoint.
- It returns undefined.

This occurs because the `network client id -> network configuration` map
was being built *after* the state update, so it was not ready at the
time of the `stateChange` event.

The fix involves moving this map building inside the state update, so
that its built by the time `stateChange` fires. But also requires deep
cloning the state before building the map from it. Otherwise we get
`Cannot perform 'get' on a proxy that has been revoked` when referencing
the ephemeral `state` lambda.


## References

<!--
Are there any issues that this pull request is tied to?
Are there other links that reviewers should consult to understand these
changes better?
Are there client or consumer pull requests to adopt any breaking
changes?

For example:

* Fixes #12345
* Related to #67890
-->

## Changelog

<!--
If you're making any consumer-facing changes, list those changes here as
if you were updating a changelog, using the template below as a guide.

(CATEGORY is one of BREAKING, ADDED, CHANGED, DEPRECATED, REMOVED, or
FIXED. For security-related issues, follow the Security Advisory
process.)

Please take care to name the exact pieces of the API you've added or
changed (e.g. types, interfaces, functions, or methods).

If there are any breaking changes, make sure to offer a solution for
consumers to follow once they upgrade to the changes.

Finally, if you're only making changes to development scripts or tests,
you may replace the template below with "None".
-->

### `@metamask/network-controller`

- **FIXED**: A race condition when calling
`getNetworkConfigurationByNetworkClientId` in response to a
`stateChange` event adding a new endpoint to a network.


## Checklist

- [ ] I've updated the test suite for new or updated code as appropriate
- [ ] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [ ] I've highlighted breaking changes using the "BREAKING" category
above as appropriate
- [ ] I've prepared draft pull requests for clients and consumer
packages to resolve any breaking changes

## Patch
### packages/network-controller/src/NetworkController.ts
```diff
@@ -22,6 +22,7 @@ import type { Hex } from '@metamask/utils';
 import { hasProperty, isPlainObject, isStrictHexString } from '@metamask/utils';
 import deepEqual from 'fast-deep-equal';
 import type { Draft } from 'immer';
+import { cloneDeep } from 'lodash';
 import type { Logger } from 'loglevel';
 import { createSelector } from 'reselect';
 import * as URI from 'uri-js';
@@ -1636,11 +1637,6 @@ export class NetworkController extends BaseController<
       });
     });
 
-    this.#networkConfigurationsByNetworkClientId =
-      buildNetworkConfigurationsByNetworkClientId(
-        this.state.networkConfigurationsByChainId,
-      );
-
     this.messagingSystem.publish(
       `${controllerName}:networkAdded`,
       newNetworkConfiguration,
@@ -1919,11 +1915,6 @@ export class NetworkController extends BaseController<
       });
     }
 
-    this.#networkConfigurationsByNetworkClientId =
-      buildNetworkConfigurationsByNetworkClientId(
-        this.state.networkConfigurationsByChainId,
-      );
-
     this.#unregisterNetworkClientsAsNeeded({
       networkClientOperations,
       autoManagedNetworkClientRegistry,
@@ -1983,11 +1974,6 @@ export class NetworkController extends BaseController<
       });
     });
 
-    this.#networkConfigurationsByNetworkClientId =
-      buildNetworkConfigurationsByNetworkClientId(
-        this.state.networkConfigurationsByChainId,
-      );
-
     this.messagingSystem.publish(
       'NetworkController:networkRemoved',
       existingNetworkConfiguration,
@@ -2500,6 +2486,11 @@ export class NetworkController extends BaseController<
       state.networkConfigurationsByChainId[args.networkFields.chainId] =
         args.networkConfigurationToPersist;
     }
+
+    this.#networkConfigurationsByNetworkClientId =
+      buildNetworkConfigurationsByNetworkClientId(
+        cloneDeep(state.networkConfigurationsByChainId),
+      );
   }
 
   /**
```

### packages/network-controller/tests/NetworkController.test.ts
```diff
@@ -11338,6 +11338,60 @@ describe('NetworkController', () => {
         });
       });
     });
+
+    it('allows calling `getNetworkConfigurationByNetworkClientId` when subscribing to state changes containing new endpoints', async () => {
+      const network = buildCustomNetworkConfiguration({
+        chainId: '0x1' as Hex,
+        name: 'mainnet',
+        nativeCurrency: 'ETH',
+        blockExplorerUrls: [],
+        defaultRpcEndpointIndex: 0,
+        rpcEndpoints: [
+          {
+            type: RpcEndpointType.Custom,
+            url: 'https://test.endpoint/1',
+            networkClientId: 'client1',
+          },
+        ],
+      });
+
+      await withController(
+        {
+          state: {
+            selectedNetworkClientId: 'client1',
+            networkConfigurationsByChainId: { '0x1': network },
+          },
+        },
+        async ({ controller, messenger }) => {
+
+          const stateChangePromise = new Promise<NetworkConfiguration | undefined>((resolve) => {
+            messenger.subscribe('NetworkController:stateChange', (state) => {
+              const { networkClientId } =
+                state.networkConfigurationsByChainId['0x1'].rpcEndpoints[1];
+
+              resolve(
+                controller.getNetworkConfigurationByNetworkClientId(networkClientId),
+              );
+            });
+          });
+
+          // Add a new endpoint
+          await controller.updateNetwork('0x1', {
+            ...network,
+            rpcEndpoints: [
+              ...network.rpcEndpoints,
+              {
+                type: RpcEndpointType.Custom,
+                url: 'https://test.endpoint/2',
+              },
+            ],
+          });
+
+          const networkConfiguration = await stateChangePromise;
+          expect(networkConfiguration).toBeDefined();
+        },
+      );
+    });
   });
 
   describe('removeNetwork', () => {
```
