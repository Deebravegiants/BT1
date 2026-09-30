# [?] Fix Deadlock with StartValidating (#1719)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-10-15
Source: https://github.com/celo-org/celo-blockchain/commit/6453534583e45cf0e082973bb68814d23a6d7b27
Type: security-commit

## Details
Fix Deadlock with StartValidating (#1719)

* Add more e2e tests to the celo-blockchain repo

* replicastate: Hold mu on NewChainHead

* Remove coreMu read lock around rs.NewChainHead

This fixes a deadlock introduced when the lock was added. This does not
introduce a unsynchronized access because coreIsStarted is an atomic.

## Patch
### .circleci/config.yml
```diff
@@ -426,6 +426,32 @@ jobs:
             export PATH=${PATH}:~/repos/golang/go/bin
             ./ci_test_validator_order.sh local ~/repos/geth
 
+  end-to-end-cip35-eth-compatibility-test:
+    executor: e2e
+    resource_class: xlarge
+    steps:
+      - attach_workspace:
+          at: ~/repos
+      - run:
+          name: End-to-end test of CIP 35
+          no_output_timeout: 15m
+          command: |
+            export PATH=${PATH}:~/repos/golang/go/bin
+            ./ci_test_cip35.sh local ~/repos/geth
+
+  end-to-end-replica-test:
+    executor: e2e
+    resource_class: xlarge
+    steps:
+      - attach_workspace:
+          at: ~/repos
+      - run:
+          name: End-to-end test of hotswap functionality
+          no_output_timeout: 15m
+          command: |
+            export PATH=${PATH}:~/repos/golang/go/bin
+            ./ci_test_replicas.sh local ~/repos/geth
+
 workflows:
   version: 2
   build:
@@ -500,3 +526,11 @@ workflows:
           requires:
             - checkout-monorepo
             - build-geth
+      - end-to-end-cip35-eth-compatibility-test:
+          requires:
+            - checkout-monorepo
+            - build-geth
+      - end-to-end-replica-test:
+          requires:
+            - checkout-monorepo
+            - build-geth
```

### consensus/istanbul/backend/engine.go
```diff
@@ -629,12 +629,10 @@ func (sb *Backend) updateReplicaStateLoop(bc *ethCore.BlockChain) {
 	for {
 		select {
 		case chainEvent := <-chainEventCh:
-			sb.coreMu.RLock()
 			if !sb.isCoreStarted() && sb.replicaState != nil {
 				consensusBlock := new(big.Int).Add(chainEvent.Block.Number(), common.Big1)
 				sb.replicaState.NewChainHead(consensusBlock)
 			}
-			sb.coreMu.RUnlock()
 		case err := <-chainEventSub.Err():
 			log.Error("Error in istanbul's subscription to the blockchain's chain event", "err", err)
 			return
```

### consensus/istanbul/backend/internal/replica/state.go
```diff
@@ -132,6 +132,9 @@ func (rs *replicaStateImpl) Close() error {
 
 // NewChainHead updates replica state and starts/stops the core if needed
 func (rs *replicaStateImpl) NewChainHead(blockNumber *big.Int) {
+	rs.mu.Lock()
+	defer rs.mu.Unlock()
+
 	logger := log.New("func", "NewChainHead", "seq", blockNumber)
 	switch rs.state {
 	case primaryInRange:
@@ -397,6 +400,10 @@ type replicaStateRLP struct {
 // not verified at the moment, but a future version might. It is
 // recommended to write only a single value but writing multiple
 // values or no value at all is also permitted.
+//
+// Note: This is called when StoreReplicaState is called so
+// mu should be held by functions that call StoreReplicaState
+// but mu should not be locked in this function.
 func (rs *replicaStateImpl) EncodeRLP(w io.Writer) error {
 	entry := replicaStateRLP{
 		State:                rs.state,
```
