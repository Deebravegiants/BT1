# [?] Fix race condition when starting up simulation tests

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-03-17
Source: https://github.com/radixdlt/babylon-node/commit/fc3bb6a1edefb924cff29db71c0a6b5a31d80eaf
Type: security-commit

## Details
Fix race condition when starting up simulation tests

## Patch
### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/SimulationTest.java
```diff
@@ -728,7 +728,7 @@ public RunningSimulationTest run(
 
     SimulationNodes bftNetwork =
         new SimulationNodes(initialNodes, simulationNetwork, baseNodeModule, overrideModules);
-    RunningNetwork runningNetwork = bftNetwork.start(disabledModuleRunners);
+    RunningNetwork runningNetwork = bftNetwork.createRunningNetwork(disabledModuleRunners);
 
     final var resultObservable =
         runChecks(runners, checkers, runningNetwork, duration)
@@ -738,6 +738,8 @@ public RunningSimulationTest run(
                   runningNetwork.stop();
                 });
 
+    runningNetwork.start();
+
     return new RunningSimulationTest(resultObservable, runningNetwork);
   }
 
```

### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/monitors/ledger/LedgerInOrderInvariant.java
```diff
@@ -68,7 +68,6 @@
 import com.radixdlt.consensus.bft.BFTNode;
 import com.radixdlt.harness.simulation.TestInvariant;
 import com.radixdlt.harness.simulation.network.SimulationNodes.RunningNetwork;
-import com.radixdlt.ledger.LedgerUpdate;
 import io.reactivex.rxjava3.core.Observable;
 import java.util.ArrayList;
 import java.util.Collections;
@@ -92,18 +91,19 @@ public Observable<TestInvariantError> check(RunningNetwork network) {
         .ledgerUpdates()
         .flatMap(
             nodeAndCommand -> {
-              BFTNode node = nodeAndCommand.getFirst();
-              LedgerUpdate ledgerUpdate = nodeAndCommand.getSecond();
-              List<Txn> nodeTxns = commandsPerNode.get(node);
+              final var node = nodeAndCommand.getFirst();
+              final var ledgerUpdate = nodeAndCommand.getSecond();
+              final var nodeTxns = commandsPerNode.computeIfAbsent(node, k -> new ArrayList<>());
               nodeTxns.addAll(ledgerUpdate.getNewTxns());
 
-              return commandsPerNode.values().stream()
-                  .filter(list -> nodeTxns != list)
-                  .filter(list -> list.size() >= nodeTxns.size())
+              return commandsPerNode.entrySet().stream()
+                  .filter(e -> nodeTxns != e.getValue())
+                  .filter(e -> e.getValue().size() >= nodeTxns.size())
                   .findFirst() // Only need to check one node, if passes, guaranteed to pass the
                   // others
                   .flatMap(
-                      list -> {
+                      e -> {
+                        var list = e.getValue();
                         if (Collections.indexOfSubList(list, nodeTxns) != 0) {
                           TestInvariantError err =
                               new TestInvariantError(
```

### radixdlt-core/radixdlt/src/integration/java/com/radixdlt/harness/simulation/network/SimulationNodes.java
```diff
@@ -192,10 +192,13 @@ public interface RunningNetwork {
 
     void runModule(BFTNode node, String name);
 
+    void start();
+
     void stop();
   }
 
-  public RunningNetwork start(ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners) {
+  public RunningNetwork createRunningNetwork(
+      ImmutableMap<BFTNode, ImmutableSet<String>> disabledModuleRunners) {
     return new RunningNetworkImpl(disabledModuleRunners);
   }
 
@@ -221,12 +224,12 @@ private class RunningNetworkImpl implements RunningNetwork {
                   Collectors.toMap(
                       p -> BFTNode.create(p.getFirst().getPublicKey()), Pair::getSecond));
 
-      nodes.entrySet().forEach(e -> init(e.getKey(), e.getValue()));
+      nodes.forEach(this::addObservables);
     }
 
-    private void init(BFTNode node, Injector injector) {
-      this.addObservables(node, injector);
-      this.startRunners(node, injector);
+    @Override
+    public void start() {
+      nodes.forEach(this::startRunners);
     }
 
     private void startRunners(BFTNode node, Injector injector) {
@@ -244,6 +247,7 @@ private void startRunners(BFTNode node, Injector injector) {
     private void addObservables(BFTNode node, Injector injector) {
       final var ledgerUpdateObservable =
           injector.getInstance(Key.get(new TypeLiteral<Observable<LedgerUpdate>>() {}));
+
       ledgerUpdateObservable.subscribe(update -> ledgerUpdates.onNext(Pair.of(node, update)));
 
       final var epochChangeObservable =
@@ -355,13 +359,15 @@ protected void configure() {
                     extraModule);
         final var injector = Guice.createInjector(module);
         this.nodes.put(bftNode, injector);
-        init(bftNode, injector);
+        this.addObservables(bftNode, injector);
+        this.startRunners(bftNode, injector);
       } else {
         final var baseModule = createBFTModule(key);
         final var module = Modules.override(baseModule).with(extraModule);
         final var injector = Guice.createInjector(module);
         this.nodes.put(bftNode, injector);
-        init(bftNode, injector);
+        this.addObservables(bftNode, injector);
+        this.startRunners(bftNode, injector);
       }
     }
 
```
