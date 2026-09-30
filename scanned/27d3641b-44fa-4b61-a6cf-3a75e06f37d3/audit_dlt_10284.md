# [?] Fix simulation test race condition, for real

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-03-21
Source: https://github.com/radixdlt/babylon-node/commit/7ec51f8af984efa117fae25ba9764274bb571323
Type: security-commit

## Details
Fix simulation test race condition, for real

## Patch
### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/network/SimulationNodes.java
```diff
@@ -99,6 +99,7 @@
 import com.radixdlt.utils.Pair;
 import io.reactivex.rxjava3.core.Maybe;
 import io.reactivex.rxjava3.core.Observable;
+import io.reactivex.rxjava3.disposables.CompositeDisposable;
 import io.reactivex.rxjava3.subjects.ReplaySubject;
 import java.util.Map;
 import java.util.Objects;
@@ -205,6 +206,9 @@ private class RunningNetworkImpl implements RunningNetwork {
 
     private final ReplaySubject<Observable<Pair<BFTNode, EpochChange>>> epochChangeObservables;
     private final ReplaySubject<Observable<Pair<BFTNode, LedgerUpdate>>> ledgerUpdateObservables;
+    private final Observable<Pair<BFTNode, EpochChange>> epochChanges;
+    private final Observable<Pair<BFTNode, LedgerUpdate>> ledgerUpdates;
+    private final CompositeDisposable epochAndLedgerUpdatesDisposable;
 
     RunningNetworkImpl(ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners) {
       this.disabledModuleRunners = disabledModuleRunners;
@@ -225,6 +229,10 @@ send in between the module runners are started and rxjava subscriber is started
       are not lost. */
       epochChangeObservables = ReplaySubject.createWithSize(nodes.size());
       ledgerUpdateObservables = ReplaySubject.createWithSize(nodes.size());
+      epochChanges = Observable.merge(epochChangeObservables).replay(1024).autoConnect();
+      ledgerUpdates = Observable.merge(ledgerUpdateObservables).replay(1024).autoConnect();
+      epochAndLedgerUpdatesDisposable =
+          new CompositeDisposable(epochChanges.subscribe(), ledgerUpdates.subscribe());
 
       nodes.forEach(this::addObservables);
       nodes.forEach(this::startRunners);
@@ -276,7 +284,7 @@ public Observable<EpochChange> latestEpochChanges() {
 
       return Observable.just(initialEpoch)
           .concatWith(
-              Observable.merge(epochChangeObservables)
+              epochChanges
                   .map(Pair::getSecond)
                   .scan(
                       (cur, next) ->
@@ -286,7 +294,7 @@ public Observable<EpochChange> latestEpochChanges() {
 
     @Override
     public Observable<Pair<BFTNode, LedgerUpdate>> ledgerUpdates() {
-      return Observable.merge(ledgerUpdateObservables);
+      return ledgerUpdates;
     }
 
     @Override
@@ -373,6 +381,7 @@ protected void configure() {
     @Override
     public void stop() {
       this.nodes.values().forEach(this::stopNode);
+      epochAndLedgerUpdatesDisposable.dispose();
     }
 
     private void stopNode(Injector injector) {
```
