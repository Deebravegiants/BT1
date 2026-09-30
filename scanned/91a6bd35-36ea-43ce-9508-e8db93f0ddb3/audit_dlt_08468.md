# [?] Fix race condition in update funding table task.  (#2895)

## Summary
Severity: Unknown
Chain: dYdX
Component: dydxprotocol/v4-chain
Published: 2025-06-11
Source: https://github.com/dydxprotocol/v4-chain/commit/9fb9c07c1c9f6eac37000484488b358e2d6094cb
Type: security-commit

## Details
Fix race condition in update funding table task.  (#2895)

## Patch
### indexer/services/roundtable/src/config.ts
```diff
@@ -161,6 +161,7 @@ export const configSchema = {
   UNCROSS_ORDERBOOK_LOCK_MULTIPLIER: parseInteger({ default: 1 }),
   PNL_TICK_UPDATE_LOCK_MULTIPLIER: parseInteger({ default: 20 }),
   SUBACCOUNT_USERNAME_GENERATOR_LOCK_MULTIPLIER: parseInteger({ default: 5 }),
+  UPDATE_FUNDING_PAYMENTS_LOCK_MULTIPLIER: parseInteger({ default: 720 }),
 
   // Maximum number of running tasks - set this equal to PG_POOL_MIN in .env, default is 2
   MAX_CONCURRENT_RUNNING_TASKS: parseInteger({ default: 2 }),
```

### indexer/services/roundtable/src/index.ts
```diff
@@ -1,14 +1,14 @@
 import { logger, startBugsnag, wrapBackgroundTask } from '@dydxprotocol-indexer/base';
 import { producer } from '@dydxprotocol-indexer/kafka';
-import { LeaderboardPnlTimeSpan, TradingRewardAggregationPeriod } from '@dydxprotocol-indexer/postgres';
+import {
+  LeaderboardPnlTimeSpan,
+  TradingRewardAggregationPeriod,
+} from '@dydxprotocol-indexer/postgres';
 
 import config from './config';
 import { complianceProvider } from './helpers/compliance-clients';
 import { startLoop } from './helpers/loops-helper';
-import {
-  redisClient,
-  connect as connectToRedis,
-} from './helpers/redis';
+import { redisClient, connect as connectToRedis } from './helpers/redis';
 import aggregateTradingRewardsTasks from './tasks/aggregate-trading-rewards';
 import cacheOrderbookMidPrices from './tasks/cache-orderbook-mid-prices';
 import cancelStaleOrdersTask from './tasks/cancel-stale-orders';
@@ -51,10 +51,7 @@ async function start(): Promise<void> {
   });
   startBugsnag();
 
-  await Promise.all([
-    producer.connect(),
-    connectToRedis(),
-  ]);
+  await Promise.all([producer.connect(), connectToRedis()]);
 
   if (config.LOOPS_ENABLED_MARKET_UPDATER) {
     startLoop(
@@ -161,11 +158,7 @@ async function start(): Promise<void> {
   );
 
   if (config.LOOPS_ENABLED_TRACK_LAG) {
-    startLoop(
-      trackLag,
-      'track_lag',
-      config.LOOPS_INTERVAL_MS_TRACK_LAG,
-    );
+    startLoop(trackLag, 'track_lag', config.LOOPS_INTERVAL_MS_TRACK_LAG);
   }
 
   if (config.LOOPS_ENABLED_REMOVE_OLD_ORDER_UPDATES) {
@@ -211,7 +204,8 @@ async function start(): Promise<void> {
 
   if (config.LOOPS_ENABLED_LEADERBOARD_PNL_ALL_TIME) {
     const allTimeLeaderboardTask: () => Promise<void> = createLeaderboardTask(
-      LeaderboardPnlTimeSpan.ALL_TIME);
+      LeaderboardPnlTimeSpan.ALL_TIME,
+    );
     startLoop(
       allTimeLeaderboardTask,
       'create_leaderboard_pnl_all_time',
@@ -220,7 +214,8 @@ async function start(): Promise<void> {
   }
   if (config.LOOPS_ENABLED_LEADERBOARD_PNL_DAILY) {
     const dailyLeaderboardTask: () => Promise<void> = createLeaderboardTask(
-      LeaderboardPnlTimeSpan.ONE_DAY);
+      LeaderboardPnlTimeSpan.ONE_DAY,
+    );
     startLoop(
       dailyLeaderboardTask,
       'create_leaderboard_pnl_daily',
@@ -229,7 +224,8 @@ async function start(): Promise<void> {
   }
   if (config.LOOPS_ENABLED_LEADERBOARD_PNL_WEEKLY) {
     const weeklyLeaderboardTask: () => Promise<void> = createLeaderboardTask(
-      LeaderboardPnlTimeSpan.SEVEN_DAYS);
+      LeaderboardPnlTimeSpan.SEVEN_DAYS,
+    );
     startLoop(
       weeklyLeaderboardTask,
       'create_leaderboard_pnl_weekly',
@@ -238,7 +234,8 @@ async function start(): Promise<void> {
   }
   if (config.LOOPS_ENABLED_LEADERBOARD_PNL_MONTHLY) {
     const monthlyLeaderboardTask: () => Promise<void> = createLeaderboardTask(
-      LeaderboardPnlTimeSpan.THIRTY_DAYS);
+      LeaderboardPnlTimeSpan.THIRTY_DAYS,
+    );
     startLoop(
       monthlyLeaderboardTask,
       'create_leaderboard_pnl_monthly',
@@ -247,7 +244,8 @@ async function start(): Promise<void> {
   }
   if (config.LOOPS_ENABLED_LEADERBOARD_PNL_YEARLY) {
     const yearlyLeaderboardTask: () => Promise<void> = createLeaderboardTask(
-      LeaderboardPnlTimeSpan.ONE_YEAR);
+      LeaderboardPnlTimeSpan.ONE_YEAR,
+    );
     startLoop(
       yearlyLeaderboardTask,
       'create_leaderboard_pnl_yearly',
@@ -294,6 +292,9 @@ async function start(): Promise<void> {
       updateFundingPaymentsTask,
       'update-funding-payments',
       config.LOOPS_INTERVAL_MS_UPDATE_FUNDING_PAYMENTS,
+      // extended lock multiplier for 12 hours since on the first run,
+      // the task takes a while to complete.
+      config.UPDATE_FUNDING_PAYMENTS_LOCK_MULTIPLIER,
     );
   }
 
```
