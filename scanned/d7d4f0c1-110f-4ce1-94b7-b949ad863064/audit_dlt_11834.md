# [?] Fix race condition with entity cache (#1873)

## Summary
Severity: Unknown
Chain: Indexer
Component: subquery/subql
Published: 2023-07-09
Source: https://github.com/subquery/subql/commit/d70228486e66be29d170bbfaa09b2c17c3d794f1
Type: security-commit

## Details
Fix race condition with entity cache (#1873)

* Fix race condition with entity cache

* Update changelog

* Fix test

* Move from using transaction to mutex for fix race condition

* Fix tests

## Patch
### packages/node-core/CHANGELOG.md
```diff
@@ -5,6 +5,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
 ## [Unreleased]
+### Fixed
+- Cache race condition when flushing cache and getting data (#1873)
 
 ## [3.1.1] - 2023-07-06
 ### Fixed
```

### packages/node-core/src/indexer/fetch.service.ts
```diff
@@ -8,7 +8,7 @@ import {Interval, SchedulerRegistry} from '@nestjs/schedule';
 import {DictionaryQueryEntry} from '@subql/types';
 import {MetaData} from '@subql/utils';
 import {range, without} from 'lodash';
-import {ApiService, IApi} from '../api.service';
+import {IApi} from '../api.service';
 import {NodeConfig} from '../configure';
 import {IndexerEvent} from '../events';
 import {getLogger} from '../logger';
@@ -138,8 +138,6 @@ export abstract class BaseFetchService<
       dictionaryValid = await this.dictionaryValidation(metadata);
     }
 
-    await Promise.all([this.getFinalizedBlockHead(), this.getBestBlockHead()]);
-
     await this.preLoopHook({valid: dictionaryValid, startHeight});
     await this.initBlockDispatcher();
 
```

### packages/node-core/src/indexer/storeCache/cacheModel.spec.ts
```diff
@@ -0,0 +1,139 @@
+// Copyright 2020-2022 OnFinality Limited authors & contributors
+// SPDX-License-Identifier: Apache-2.0
+
+import {delay} from '@subql/common';
+import {Sequelize} from '@subql/x-sequelize';
+import {NodeConfig} from '../../configure';
+import {CachedModel} from './cacheModel';
+
+jest.mock('@subql/x-sequelize', () => {
+  let data: Record<string, any> = {};
+
+  let pendingData: typeof data = {};
+  let afterCommitHooks: Array<() => void> = [];
+
+  const mSequelize = {
+    authenticate: jest.fn(),
+    Op: {
+      in: jest.fn(),
+      notIn: jest.fn(),
+    },
+    define: () => ({
+      findOne: jest.fn(),
+      create: (input: any) => input,
+    }),
+    query: () => [{nextval: 1}],
+    showAllSchemas: () => ['subquery_1'],
+    model: (entity: string) => ({
+      upsert: jest.fn(),
+      associations: [{}, {}],
+      count: 5,
+      findAll: [
+        {
+          id: 'apple-05-sequelize',
+          field1: 'set apple at block 5 with sequelize',
+        },
+      ],
+      findOne: jest.fn(({transaction, where: {id}}) => ({
+        toJSON: () => (transaction ? pendingData[id] ?? data[id] : data[id]),
+      })),
+      bulkCreate: jest.fn((records: {id: string}[]) => {
+        records.map((r) => (pendingData[r.id] = r));
+      }),
+      destroy: jest.fn(),
+    }),
+    sync: jest.fn(),
+    transaction: () => ({
+      commit: jest.fn(async () => {
+        await delay(1);
+        data = {...data, ...pendingData};
+        pendingData = {};
+        afterCommitHooks.map((fn) => fn());
+        afterCommitHooks = [];
+      }), // Delay of 1s is used to test whether we wait for cache to flush
+      rollback: jest.fn(),
+      afterCommit: jest.fn((fn) => afterCommitHooks.push(fn)),
+    }),
+    // createSchema: jest.fn(),
+  };
+  const actualSequelize = jest.requireActual('@subql/x-sequelize');
+  return {
+    Sequelize: jest.fn(() => mSequelize),
+    DataTypes: actualSequelize.DataTypes,
+    QueryTypes: actualSequelize.QueryTypes,
+    Deferrable: actualSequelize.Deferrable,
+  };
+});
+
+describe('cacheModel', () => {
+  describe('without historical', () => {
+    let testModel: CachedModel<{id: string; field1: number}>;
+    let sequelize: Sequelize;
+
+    const flush = async () => {
+      const tx = await sequelize.transaction();
+
+      await testModel.flush(tx);
+
+      return tx.commit();
+    };
+
+    beforeEach(() => {
+      let i = 0;
+      sequelize = new Sequelize();
+      testModel = new CachedModel(sequelize.model('entity1'), false, {} as NodeConfig);
+      testModel.init(() => i++);
+    });
+
+    it('can avoid race conditions', async () => {
+      // Set the initial model, so we have data in the DB
+      testModel.set(
+        'entity1_id_0x01',
+        {
+          id: 'entity1_id_0x01',
+          field1: 1,
+        },
+        1
+      );
+      await flush();
+
+      // Get the entity and update again so we can have a difference between db and cache
+      const entity1 = await testModel.get('entity1_id_0x01');
+      if (!entity1) {
+        throw new Error('Entity should exist');
+      }
+
+      testModel.set(
+        'entity1_id_0x01',
+        {
+          ...entity1,
+          field1: entity1.field1 + 1,
+        },
+        2
+      );
+
+      // Clear the get cache to simulate many other operations happening
+      (testModel as any).getCache.clear();
+
+      // Flush and update the entity at the same time
+      const pendingFlush = flush();
+
+      await delay(0.2);
+      const entity2 = await testModel.get('entity1_id_0x01');
+
+      testModel.set(
+        'entity1_id_0x01',
+        {
+          id: 'entity1_id_0x01',
+          field1: (entity2?.field1 ?? 0) + 1,
+        },
+        3
+      );
+
+      await pendingFlush;
+
+      const finalEntity = await testModel.get('entity1_id_0x01');
+      expect(finalEntity?.field1).toEqual(3);
+    });
+  });
+});
```

### packages/node-core/src/indexer/storeCache/cacheModel.ts
```diff
@@ -3,6 +3,7 @@
 
 import {CreationAttributes, Model, ModelStatic, Op, Sequelize, Transaction} from '@subql/x-sequelize';
 import {Fn} from '@subql/x-sequelize/types/utils';
+import {Mutex} from 'async-mutex';
 import {flatten, includes, isEqual, uniq} from 'lodash';
 import {NodeConfig} from '../../configure';
 import {SetValueModel} from './setValueModel';
@@ -32,6 +33,7 @@ export class CachedModel<
   private removeCache: Record<string, RemoveValue> = {};
   private _getNextStoreOperationIndex?: () => number;
   readonly hasAssociations: boolean = false;
+  private mutex = new Mutex();
 
   flushableRecordCounter = 0;
 
@@ -78,6 +80,7 @@ export class CachedModel<
       // Then we try look from setCache
       let record = this.setCache[id]?.getLatest()?.data;
       if (!record) {
+        await this.mutex.waitForUnlock();
         record = (
           await this.model.findOne({
             // https://github.com/sequelize/sequelize/issues/15179
@@ -119,6 +122,7 @@ export class CachedModel<
       options.limit = options.limit - (cachedData.length - options.offset);
     }
 
+    await this.mutex.waitForUnlock();
     const records = await this.model.findAll({
       where: {[field]: value, id: {[Op.notIn]: this.allCachedIds()}} as any,
       limit: options?.limit, //limit should pass from store
@@ -142,6 +146,7 @@ export class CachedModel<
       if (oneFromCached) {
         return oneFromCached;
       } else {
+        await this.mutex.waitForUnlock();
         const record = (
           await this.model.findOne({
             where: {[field]: value, id: {[Op.notIn]: this.allCachedIds()}} as any,
@@ -211,61 +216,69 @@ export class CachedModel<
   }
 
   async flush(tx: Transaction, blockHeight?: number): Promise<void> {
-    // Get records relevant to the block height
-    const {removeRecords, setRecords} = blockHeight
-      ? this.filterRecordsWithHeight(blockHeight)
-      : {removeRecords: this.removeCache, setRecords: this.setCache};
-    // Filter non-historical could return undefined due to it been removed
-    let records = this.applyBlockRange(setRecords).filter((r) => !!r);
-    let dbOperation: Promise<unknown>;
-    if (this.historical) {
-      dbOperation = Promise.all([
-        // set, bulkCreate, bulkUpdate & remove close previous records
-        this.historicalMarkPreviousHeightRecordsBatch(tx, setRecords, removeRecords),
-        // bulkCreate all new records for this entity,
-        // include(set, bulkCreate, bulkUpdate)
-        this.model.bulkCreate(records, {
-          transaction: tx,
-        }),
-      ]);
-    } else {
-      // We need to check within the same model if there is multiple operations (set/remove) to the same id
-      // we don't have to consider the order in setCache, as we are using getLatest()?.data;
-      // also in removeCache only store last remove operation too.
-
-      // If same Id exist in both set and remove records, we only need to pick the last operation for this ID,
-      // As both cache in final status, so we can compare their operation index
-      for (const v of Object.values(setRecords)) {
-        const latestSet = v.getLatest();
-        if (latestSet !== undefined && removeRecords[latestSet.data.id]) {
-          if (removeRecords[latestSet.data.id].operationIndex > latestSet.operationIndex) {
-            records = records.filter((r) => r.id !== latestSet.data.id);
-          } else if (removeRecords[latestSet.data.id].operationIndex < latestSet.operationIndex) {
-            delete removeRecords[latestSet.data.id];
-          } else {
-            throw new Error(
-              `Cache entity ${this.model.name} Id ${latestSet.data.id} has same Operation Indexes in remove and set cache `
-            );
-          }
-        }
-      }
-
-      dbOperation = Promise.all([
-        records.length &&
+    const release = await this.mutex.acquire();
+
+    try {
+      tx.afterCommit(() => release());
+      // Get records relevant to the block height
+      const {removeRecords, setRecords} = blockHeight
+        ? this.filterRecordsWithHeight(blockHeight)
+        : {removeRecords: this.removeCache, setRecords: this.setCache};
+      // Filter non-historical could return undefined due to it been removed
+      let records = this.applyBlockRange(setRecords).filter((r) => !!r);
+      let dbOperation: Promise<unknown>;
+      if (this.historical) {
+        dbOperation = Promise.all([
+          // set, bulkCreate, bulkUpdate & remove close previous records
+          this.historicalMarkPreviousHeightRecordsBatch(tx, setRecords, removeRecords),
+          // bulkCreate all new records for this entity,
+          // include(set, bulkCreate, bulkUpdate)
           this.model.bulkCreate(records, {
             transaction: tx,
-            updateOnDuplicate: Object.keys(records[0]) as unknown as (keyof T)[],
           }),
-        Object.keys(removeRecords).length &&
-          this.model.destroy({where: {id: Object.keys(removeRecords)} as any, transaction: tx}),
-      ]);
-    }
+        ]);
+      } else {
+        // We need to check within the same model if there is multiple operations (set/remove) to the same id
+        // we don't have to consider the order in setCache, as we are using getLatest()?.data;
+        // also in removeCache only store last remove operation too.
+
+        // If same Id exist in both set and remove records, we only need to pick the last operation for this ID,
+        // As both cache in final status, so we can compare their operation index
+        for (const v of Object.values(setRecords)) {
+          const latestSet = v.getLatest();
+          if (latestSet !== undefined && removeRecords[latestSet.data.id]) {
+            if (removeRecords[latestSet.data.id].operationIndex > latestSet.operationIndex) {
+              records = records.filter((r) => r.id !== latestSet.data.id);
+            } else if (removeRecords[latestSet.data.id].operationIndex < latestSet.operationIndex) {
+              delete removeRecords[latestSet.data.id];
+            } else {
+              throw new Error(
+                `Cache entity ${this.model.name} Id ${latestSet.data.id} has same Operation Indexes in remove and set cache `
+              );
+            }
+          }
+        }
 
-    // Don't await DB operations to complete before clearing.
-    // This allows new data to be cached while flushing
-    this.clear(blockHeight);
+        dbOperation = Promise.all([
+          records.length &&
+            this.model.bulkCreate(records, {
+              transaction: tx,
+              updateOnDuplicate: Object.keys(records[0]) as unknown as (keyof T)[],
+            }),
+          Object.keys(removeRecords).length &&
+            this.model.destroy({where: {id: Object.keys(removeRecords)} as any, transaction: tx}),
+        ]);
+      }
+
+      // Don't await DB operations to complete before clearing.
+      // This allows new data to be cached while flushing
+      this.clear(blockHeight);
 
-    await dbOperation;
+      await dbOperation;
+    } catch (e) {
+      release();
+      throw e;
+    }
   }
 
   // Flush relation model in operationIndex order with non-historical db
```

### packages/node-core/src/indexer/storeCache/setValueModel.ts
```diff
@@ -27,7 +27,9 @@ export class SetValueModel<T> {
       if (this.historicalValues[latestIndex].startHeight === blockHeight) {
         this.historicalValues[latestIndex].data = data;
       } else if (this.historicalValues[latestIndex].startHeight > blockHeight) {
-        throw new Error(`Can not set record with block height ${blockHeight}`);
+        throw new Error(
+          `Can not set record with block height ${blockHeight} as data for future block heights has been set`
+        );
       } else {
         this.historicalValues[latestIndex].endHeight = blockHeight;
         this.create(data, blockHeight, operationIndex);
```

### packages/node-core/src/indexer/storeCache/storeCache.service.spec.ts
```diff
@@ -295,14 +295,14 @@ describe('Store Cache flush with non-historical', () => {
   let storeService: StoreCacheService;
 
   const sequilize = new Sequelize();
-  const nodeConfig: NodeConfig = {disableHistorical: false} as any;
+  const nodeConfig: NodeConfig = {disableHistorical: true} as any;
 
   beforeEach(() => {
     storeService = new StoreCacheService(sequilize, nodeConfig, eventEmitter, new SchedulerRegistry());
     storeService.init(false, false);
   });
 
-  it('Same Id with multiple operations, when flush it should always pick up the latest operation', () => {
+  it.only('Same Id with multiple operations, when flush it should always pick up the latest operation', async () => {
     const entity1Model = storeService.getModel('entity1');
 
     //create Id 1
@@ -329,19 +329,20 @@ describe('Store Cache flush with non-historical', () => {
     );
 
     //simulate flush here
-    (entity1Model as any).flush(undefined, 5);
+    const tx = await sequilize.transaction();
+    await (entity1Model as any).flush(tx, 5);
 
     const sequelizeModel1 = (entity1Model as any).model;
     const spyModel1Create = jest.spyOn(sequelizeModel1, 'bulkCreate');
     const spyModel1Destroy = jest.spyOn(sequelizeModel1, 'destroy');
 
     // Only last set record with block 5 is created
     expect(spyModel1Create).toHaveBeenCalledWith([{field1: 'set at block 5', id: 'entity1_id_0x01'}], {
-      transaction: undefined,
+      transaction: tx,
       updateOnDuplicate: ['id', 'field1'],
     });
     // remove id 2 only
-    expect(spyModel1Destroy).toHaveBeenCalledWith({transaction: undefined, where: {id: ['entity1_id_0x02']}});
+    expect(spyModel1Destroy).toHaveBeenCalledWith({transaction: tx, where: {id: ['entity1_id_0x02']}});
   });
 });
 
```
