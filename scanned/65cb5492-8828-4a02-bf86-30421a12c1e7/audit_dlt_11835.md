# [?] fix workers crashes error (#1642)

## Summary
Severity: Unknown
Chain: Indexer
Component: subquery/subql
Published: 2023-04-25
Source: https://github.com/subquery/subql/commit/e53bd983bbbf21ab18ef562eaf9d33fb11d62f60
Type: security-commit

## Details
fix workers crashes error (#1642)

* try to fix workers

* Fix dependency injection

---------

Co-authored-by: Scott Twiname <skott.twiname@gmail.com>

## Patch
### packages/node-core/src/indexer/mmr.service.ts
```diff
@@ -57,7 +57,7 @@ export class MmrService implements OnApplicationShutdown {
   }
 
   private get blockOffset(): number {
-    if (!this._blockOffset) {
+    if (this._blockOffset === undefined) {
       throw new Error('MMR Service sync has not been called');
     }
     return this._blockOffset;
```

### packages/node/src/indexer/fetch.service.ts
```diff
@@ -264,11 +264,15 @@ export class FetchService implements OnApplicationShutdown {
 
     await this.syncDynamicDatascourcesFromMeta();
 
-    this.updateDictionary();
-    //  Call metadata here, other network should align with this
-    //  For substrate, we might use the specVersion metadata in future if we have same error handling as in node-core
-    const metadata = await this.dictionaryService.getMetadata();
-    const dictionaryValid = this.dictionaryValidation(metadata);
+    let dictionaryValid = false;
+
+    if (this.project.network.dictionary) {
+      this.updateDictionary();
+      //  Call metadata here, other network should align with this
+      //  For substrate, we might use the specVersion metadata in future if we have same error handling as in node-core
+      const metadata = await this.dictionaryService.getMetadata();
+      dictionaryValid = this.dictionaryValidation(metadata);
+    }
 
     await Promise.all([this.getFinalizedBlockHead(), this.getBestBlockHead()]);
 
```

### packages/node/src/indexer/runtime/base-runtime.service.ts
```diff
@@ -4,10 +4,11 @@
 import { Injectable, OnApplicationShutdown } from '@nestjs/common';
 import { ApiPromise } from '@polkadot/api';
 import { RuntimeVersion } from '@polkadot/types/interfaces';
-import { profiler, ApiService } from '@subql/node-core';
+import { profiler } from '@subql/node-core';
 import { SubstrateBlock } from '@subql/types';
 import * as SubstrateUtil from '../../utils/substrate';
 import { yargsOptions } from '../../yargs';
+import { ApiService } from '../api.service';
 import { SpecVersion } from './../dictionary.service';
 export const SPEC_VERSION_BLOCK_GAP = 100;
 type GetUseDictionary = () => boolean;
```
