# [?] Fix simulation tests events race condition

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-03-18
Source: https://github.com/radixdlt/babylon-node/commit/a6d5327ca90b67535b8f47b8efd93ab2ac173461
Type: security-commit

## Details
Fix simulation tests events race condition

## Patch
### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/SimulationTest.java
```diff
@@ -730,7 +730,7 @@ public RunningSimulationTest run(
 
     SimulationNodes bftNetwork =
         new SimulationNodes(initialNodes, simulationNetwork, baseNodeModule, overrideModules);
-    RunningNetwork runningNetwork = bftNetwork.createRunningNetwork(disabledModuleRunners);
+    RunningNetwork runningNetwork = bftNetwork.start(disabledModuleRunners);
 
     final var resultObservable =
         runChecks(runners, checkers, runningNetwork, duration)
@@ -740,8 +740,6 @@ public RunningSimulationTest run(
                   runningNetwork.stop();
                 });
 
-    runningNetwork.start();
-
     return new RunningSimulationTest(resultObservable, runningNetwork);
   }
 
```

### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/monitors/ledger/LedgerInOrderInvariant.java
```diff
@@ -75,12 +75,15 @@
 import java.util.List;
 import java.util.Map;
 import java.util.Optional;
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
 
 /**
  * Ledger-side safety check. Checks that commands and the order getting persisted are the same
  * across all nodes.
  */
 public class LedgerInOrderInvariant implements TestInvariant {
+  private static final Logger log = LogManager.getLogger();
 
   @Override
   public Observable<TestInvariantError> check(RunningNetwork network) {
@@ -103,11 +106,18 @@ public Observable<TestInvariantError> check(RunningNetwork network) {
                   // others
                   .flatMap(
                       e -> {
-                        var list = e.getValue();
-                        if (Collections.indexOfSubList(list, nodeTxns) != 0) {
-                          TestInvariantError err =
-                              new TestInvariantError(
-                                  "Two nodes don't agree on commands: " + list + " " + nodeTxns);
+                        var otherNode = e.getKey();
+                        var otherNodeTxns = e.getValue();
+                        if (Collections.indexOfSubList(otherNodeTxns, nodeTxns) != 0) {
+                          log.info(
+                              "Two nodes don't agree on commands. Node {} has commands {} but node"
+                                  + " {} has {}",
+                              node,
+                              nodeTxns,
+                              otherNode,
+                              otherNodeTxns);
+                          final var err =
+                              new TestInvariantError("Two nodes don't agree on commands");
                           return Optional.of(Observable.just(err));
                         }
                         return Optional.empty();
```

### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/network/SimulationNodes.java
```diff
@@ -99,7 +99,7 @@
 import com.radixdlt.utils.Pair;
 import io.reactivex.rxjava3.core.Maybe;
 import io.reactivex.rxjava3.core.Observable;
-import io.reactivex.rxjava3.subjects.PublishSubject;
+import io.reactivex.rxjava3.subjects.ReplaySubject;
 import java.util.Map;
 import java.util.Objects;
 import java.util.stream.Collectors;
@@ -192,23 +192,19 @@ public interface RunningNetwork {
 
     void runModule(BFTNode node, String name);
 
-    void start();
-
     void stop();
   }
 
-  public RunningNetwork createRunningNetwork(
-      ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners) {
+  public RunningNetwork start(ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners) {
     return new RunningNetworkImpl(disabledModuleRunners);
   }
 
   private class RunningNetworkImpl implements RunningNetwork {
     private final ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners;
     private final Map<BFTNode, Injector> nodes;
 
-    private final PublishSubject<Pair<BFTNode, EpochChange>> epochChanges = PublishSubject.create();
-    private final PublishSubject<Pair<BFTNode, LedgerUpdate>> ledgerUpdates =
-        PublishSubject.create();
+    private final ReplaySubject<Observable<Pair<BFTNode, EpochChange>>> epochChangeObservables;
+    private final ReplaySubject<Observable<Pair<BFTNode, LedgerUpdate>>> ledgerUpdateObservables;
 
     RunningNetworkImpl(ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners) {
       this.disabledModuleRunners = disabledModuleRunners;
@@ -224,11 +220,13 @@ private class RunningNetworkImpl implements RunningNetwork {
                   Collectors.toMap(
                       p -> BFTNode.create(p.getFirst().getPublicKey()), Pair::getSecond));
 
-      nodes.forEach(this::addObservables);
-    }
+      /* Using ReplaySubject so that the initial events that are
+      send in between the module runners are started and rxjava subscriber is started (in awaitCompletion)
+      are not lost. */
+      epochChangeObservables = ReplaySubject.createWithSize(nodes.size());
+      ledgerUpdateObservables = ReplaySubject.createWithSize(nodes.size());
 
-    @Override
-    public void start() {
+      nodes.forEach(this::addObservables);
       nodes.forEach(this::startRunners);
     }
 
@@ -248,15 +246,16 @@ private void addObservables(BFTNode node, Injector injector) {
       final var ledgerUpdateObservable =
           injector.getInstance(Key.get(new TypeLiteral<Observable<LedgerUpdate>>() {}));
 
-      ledgerUpdateObservable.subscribe(update -> ledgerUpdates.onNext(Pair.of(node, update)));
+      ledgerUpdateObservables.onNext(
+          ledgerUpdateObservable.map(ledgerUpdate -> Pair.of(node, ledgerUpdate)));
 
       final var epochChangeObservable =
           ledgerUpdateObservable.flatMapMaybe(
               ledgerUpdate -> {
                 final var e = ledgerUpdate.getStateComputerOutput().getInstance(EpochChange.class);
                 return e == null ? Maybe.empty() : Maybe.just(Pair.of(node, e));
               });
-      epochChangeObservable.subscribe(epochChanges::onNext);
+      epochChangeObservables.onNext(epochChangeObservable);
     }
 
     @Override
@@ -277,7 +276,7 @@ public Observable<EpochChange> latestEpochChanges() {
 
       return Observable.just(initialEpoch)
           .concatWith(
-              epochChanges
+              Observable.merge(epochChangeObservables)
                   .map(Pair::getSecond)
                   .scan(
                       (cur, next) ->
@@ -287,7 +286,7 @@ public Observable<EpochChange> latestEpochChanges() {
 
     @Override
     public Observable<Pair<BFTNode, LedgerUpdate>> ledgerUpdates() {
-      return ledgerUpdates;
+      return Observable.merge(ledgerUpdateObservables);
     }
 
     @Override
```

### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/integration/steady_state/simulation/full_function_forks/OutdatedNodeForksTest.java
```diff
@@ -89,9 +89,11 @@
 import com.radixdlt.statecomputer.forks.RadixEngineForksGenesisOnlyModule;
 import com.radixdlt.sync.SyncConfig;
 import com.radixdlt.utils.UInt256;
+import io.reactivex.rxjava3.schedulers.Schedulers;
 import java.time.Duration;
 import java.util.Collections;
 import java.util.Set;
+import java.util.concurrent.Executors;
 import java.util.concurrent.TimeUnit;
 import java.util.concurrent.atomic.AtomicReference;
 import java.util.function.Consumer;
@@ -153,9 +155,12 @@ public void outdated_node_should_recover_when_restarted_with_missing_forks() {
         };
 
     final var latestEpochChange = new AtomicReference<EpochChange>();
+    final var testExecutor = Executors.newSingleThreadExecutor();
     final var testErrorsDisposable =
         network
             .latestEpochChanges()
+            /* required so that when the bft runner restarts at epoch 12 it doesn't happen at the bft runner thread */
+            .observeOn(Schedulers.from(testExecutor))
             .subscribe(
                 epochChange -> {
                   latestEpochChange.set(epochChange);
@@ -231,5 +236,7 @@ protected void configure() {
 
     // just a sanity check to make sure that at least 14 epochs have passed
     assertTrue(latestEpochChange.get().getEpoch() > 14);
+
+    testExecutor.shutdownNow();
   }
 }
```

### radixdlt-core/radixdlt/src/main/java/com/radixdlt/statecomputer/forks/Forks.java
```diff
@@ -453,7 +453,7 @@ public static boolean testCandidate(
               .map(
                   currentForkVotingResult ->
                       previousVotingResultsCursor.concat(
-                          () -> CloseableCursor.of(currentForkVotingResult)))
+                          () -> CloseableCursor.single(currentForkVotingResult)))
               .orElse(previousVotingResultsCursor);
       return testCandidate(
           candidateFork, ledgerAndBFTProof.getProof(), previousAndCurrentResultsCursor);
```

### radixdlt-core/radixdlt/src/test/java/com/radixdlt/api/service/ForkVoteStatusServiceTest.java
```diff
@@ -150,8 +150,7 @@ public void should_not_require_a_vote_for_non_candidate_fork() {
 
   private CloseableCursor<RawSubstateBytes> votesOf(
       CandidateForkConfig forkConfig, BFTNode... nodes) {
-    return CloseableCursor.of(
-        Arrays.stream(nodes).map(n -> voteOf(n, forkConfig)).toArray(RawSubstateBytes[]::new));
+    return CloseableCursor.of(Arrays.stream(nodes).map(n -> voteOf(n, forkConfig)).toList());
   }
 
   private RawSubstateBytes voteOf(BFTNode validator, CandidateForkConfig forkConfig) {
```

### radixdlt-engine/src/main/java/com/radixdlt/atom/CloseableCursor.java
```diff
@@ -194,9 +194,8 @@ public T next() {
     };
   }
 
-  @SafeVarargs
-  static <T> CloseableCursor<T> of(T... items) {
-    return of(List.of(items));
+  static <T> CloseableCursor<T> single(T item) {
+    return of(List.of(item));
   }
 
   static <T> CloseableCursor<T> of(List<T> items) {
```

### radixdlt-engine/src/main/java/com/radixdlt/store/InMemoryEngineStore.java
```diff
@@ -114,7 +114,7 @@ public InMemoryEngineStore() {
   public <R> R transaction(TransactionEngineStoreConsumer<M, R> consumer)
       throws RadixEngineException {
     return consumer.start(
-        new EngineStoreInTransaction<M>() {
+        new EngineStoreInTransaction<>() {
           @Override
           public void storeTxn(REProcessedTxn txn) {
             synchronized (lock) {
```
