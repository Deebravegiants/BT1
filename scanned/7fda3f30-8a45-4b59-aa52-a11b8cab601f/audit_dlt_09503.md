# [?] fix: remove race condition in bouncer observe event (#6023)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-08-04
Source: https://github.com/chainflip-io/chainflip-backend/commit/ecb2caa039bacd403c0dad146ba9ffa8b5a500ed
Type: security-commit

## Details
fix: remove race condition in bouncer observe event (#6023)

* fix: remove race condition between historic blocks checking and new block subscription

* fix: properly convert header.number to number

## Patch
### bouncer/shared/utils/substrate.ts
```diff
@@ -126,6 +126,12 @@ export type Event<T = any> = {
   eventIndex: number;
 };
 
+type SubscriptionItem = {
+  blockHash: string;
+  blockNumber: number;
+  events: Event[];
+};
+
 // Iterate over all the events, reshaping them for the consumer
 // eslint-disable-next-line @typescript-eslint/no-explicit-any
 function mapEvents(events: any[], blockNumber: number): Event[] {
@@ -317,7 +323,7 @@ const subscribeHeads = getCachedDisposable(
     // Take the correct substrate API
     const api = stack.use(await apiMap[chain]());
 
-    const subject = new Subject<Event[]>();
+    const subject = new Subject<SubscriptionItem>();
 
     // subscribe to the correct head based on the finalized flag
     const subscribe = finalized
@@ -331,15 +337,19 @@ const subscribeHeads = getCachedDisposable(
       const mappedEvents = mapEvents(rawEvents, header.number.toNumber());
       const cache = eventCacheMap[chain];
       cache.addEvents(header.hash.toString(), mappedEvents, finalized);
-      subject.next(mappedEvents);
+      subject.next({
+        blockHash: header.hash.toString(),
+        blockNumber: header.number.toNumber(),
+        events: mappedEvents,
+      });
     });
 
     // automatic cleanup!
     stack.defer(unsubscribe);
     stack.defer(() => subject.complete());
 
     return {
-      observable: subject as Observable<Event[]>,
+      observable: subject as Observable<SubscriptionItem>,
       [Symbol.asyncDispose]() {
         return stack.disposeAsync();
       },
@@ -350,13 +360,11 @@ const subscribeHeads = getCachedDisposable(
 async function getPastEvents(
   chain: SubstrateChain,
   historicalCheckBlocks: number,
+  latestBlockNumber: number,
 ): Promise<Event[]> {
   if (historicalCheckBlocks <= 0) {
     throw new Error('Invalid Historical Check Blocks');
   }
-  const api = await apiMap[chain]();
-  const latestHeader = await api.rpc.chain.getHeader();
-  const latestBlockNumber = latestHeader.number.toNumber();
   const startAtBlock = Math.max(latestBlockNumber - historicalCheckBlocks, 0);
   const cache = eventCacheMap[chain];
   return cache.getEvents(startAtBlock, latestBlockNumber);
@@ -423,36 +431,45 @@ export function observeEvents<T = any>(
   const findEvent = async () => {
     const foundEvents: Event[] = [];
 
-    // Check historic events first
-    if (historicalCheckBlocks > 0) {
-      const historicEvents = await getPastEvents(chain, historicalCheckBlocks);
-      for (const event of historicEvents) {
-        if (
-          event.name.section.includes(expectedSection) &&
-          event.name.method.includes(expectedMethod) &&
-          test(event)
-        ) {
-          foundEvents.push(event);
-        }
-      }
-    }
-    if (foundEvents.length > 0) {
-      logger.trace(
-        `Found event ${foundEvents.length} ${eventName} events in block ${foundEvents[0].block}`,
-      );
-      // No need to continue if we found event(s) in the past
-      return foundEvents;
-    }
-
     const findEventSubscription = async () => {
       // Subscribe to new events and wait for the first match
       await using subscription = await subscribeHeads({ chain, finalized });
       const subscriptionIterator = observableToIterable(
         subscription.observable,
         controller?.signal,
       );
-      for await (const events of subscriptionIterator) {
-        for (const event of events) {
+      let isInitialBlock = true;
+      for await (const subscriptionItem of subscriptionIterator) {
+        if (isInitialBlock) {
+          isInitialBlock = false;
+
+          // Check historic events first
+          if (historicalCheckBlocks > 0) {
+            const historicEvents = await getPastEvents(
+              chain,
+              historicalCheckBlocks,
+              subscriptionItem.blockNumber,
+            );
+            for (const event of historicEvents) {
+              if (
+                event.name.section.includes(expectedSection) &&
+                event.name.method.includes(expectedMethod) &&
+                test(event)
+              ) {
+                foundEvents.push(event);
+              }
+            }
+          }
+          if (foundEvents.length > 0) {
+            logger.trace(
+              `Found event ${foundEvents.length} ${eventName} events in block ${foundEvents[0].block}`,
+            );
+            // No need to continue if we found event(s) in the past
+            return foundEvents;
+          }
+        }
+
+        for (const event of subscriptionItem.events) {
           if (
             event.name.section.includes(expectedSection) &&
             event.name.method.includes(expectedMethod) &&
```
