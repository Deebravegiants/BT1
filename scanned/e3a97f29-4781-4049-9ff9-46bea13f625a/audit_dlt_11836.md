# [?] [node] fix memory overflow while indexing a large number of event/call in a single block (#190)

## Summary
Severity: Unknown
Chain: Indexer
Component: subquery/subql
Published: 2021-02-22
Source: https://github.com/subquery/subql/commit/14445b5be8b825c23cc2733e8428806c76e4b579
Type: security-commit

## Details
[node] fix memory overflow while indexing a large number of event/call in a single block (#190)

* [node] Fix memory overflow while indexing a large number of events in a single block.

* [node] use for loop for handler

## Patch
### packages/node/src/indexer/fetch.service.ts
```diff
@@ -7,7 +7,7 @@ import { ApiPromise } from '@polkadot/api';
 import { isUndefined } from 'lodash';
 import { NodeConfig } from '../configure/NodeConfig';
 import { getLogger } from '../utils/logger';
-import { delay, timeout } from '../utils/promise';
+import { delay } from '../utils/promise';
 import * as SubstrateUtil from '../utils/substrate';
 import { ApiService } from './api.service';
 import { BlockedQueue } from './BlockedQueue';
@@ -54,7 +54,7 @@ export class FetchService implements OnApplicationShutdown {
         let success = false;
         while (!success) {
           try {
-            await timeout(next(block), 10);
+            await next(block);
             success = true;
           } catch (e) {
             logger.error(
```

### packages/node/src/indexer/indexer.manager.ts
```diff
@@ -12,6 +12,7 @@ import { SubqueryProject } from '../configure/project.model';
 import { SubqueryModel, SubqueryRepo } from '../entities';
 import { objectTypeToModelAttributes } from '../utils/graphql';
 import { getLogger } from '../utils/logger';
+import { timeout } from '../utils/promise';
 import * as SubstrateUtil from '../utils/substrate';
 import { ApiService } from './api.service';
 import { IndexerEvent } from './events';
@@ -49,7 +50,7 @@ export class IndexerManager {
     const tx = await this.sequelize.transaction();
     this.storeService.setTransaction(tx);
     try {
-      await this.apiService.setBlockhash(block.block.hash);
+      await timeout(this.apiService.setBlockhash(block.block.hash), 10); //TODO remove this when polkadot/api issue #3197 solved
       for (const ds of this.project.dataSources) {
         if (ds.startBlock > block.block.header.number.toNumber()) {
           continue;
@@ -67,23 +68,19 @@ export class IndexerManager {
                   extrinsics,
                   handler.filter,
                 );
-                await Promise.all(
-                  filteredExtrinsics.map(async (e) =>
-                    this.vm.securedExec(handler.handler, [e]),
-                  ),
-                );
+                for (const e of filteredExtrinsics) {
+                  await this.vm.securedExec(handler.handler, [e]);
+                }
                 break;
               }
               case SubqlKind.EventHandler: {
                 const filteredEvents = SubstrateUtil.filterEvents(
                   events,
                   handler.filter,
                 );
-                await Promise.all(
-                  filteredEvents.map(async (e) =>
-                    this.vm.securedExec(handler.handler, [e]),
-                  ),
-                );
+                for (const e of filteredEvents) {
+                  await this.vm.securedExec(handler.handler, [e]);
+                }
                 break;
               }
               default:
```

### packages/node/src/indexer/sandbox.ts
```diff
@@ -9,6 +9,7 @@ import { merge } from 'lodash';
 import { NodeVM, NodeVMOptions, VMScript } from 'vm2';
 import { NodeConfig } from '../configure/NodeConfig';
 import { levelFilter } from '../utils/logger';
+import { timeout } from '../utils/promise';
 
 export interface SandboxOption {
   store: Store;
@@ -76,7 +77,7 @@ export class IndexerSandbox extends NodeVM {
     this.setGlobal('args', args);
     this.setGlobal('funcName', funcName);
     try {
-      await this.run(this.script);
+      await timeout(this.run(this.script), 10);
     } catch (e) {
       e.handler = funcName;
       if (
```
