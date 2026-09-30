# [?] Fix a deadlock bug   (#1866)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2020-02-07
Source: https://github.com/iotexproject/iotex-core/commit/0727a1eae44373ad5099bb55ed06bb2827696790
Type: security-commit

## Details
Fix a deadlock bug   (#1866)

* fix a deadlock bug in state factory

## Patch
### state/factory/factory.go
```diff
@@ -204,24 +204,18 @@ func (sf *factory) NewWorkingSet() (WorkingSet, error) {
 }
 
 func (sf *factory) Validate(ctx context.Context, blk *block.Block) error {
-	sf.mutex.Lock()
-	defer sf.mutex.Unlock()
 	key := generateWorkingSetCacheKey(blk.Header, blk.Header.ProducerAddress())
-	if data, ok := sf.workingsets.Get(key); ok {
-		if _, ok := data.(WorkingSet); !ok {
-			return errors.New("type assertion failed to be WorkingSet")
-		}
-		// if already validated, return nil
-		return nil
-	}
-	ws, err := newWorkingSet(sf.currentChainHeight+1, sf.dao, sf.rootHash(), sf.saveHistory)
+	ws, isExist, err := sf.getFromWorkingSets(key)
 	if err != nil {
-		return errors.Wrap(err, "failed to obtain working set from state factory")
+		return err
+	}
+	if isExist {
+		return nil
 	}
 	if err := validateWithWorkingset(ctx, ws, blk); err != nil {
 		return errors.Wrap(err, "failed to validate block with workingset in factory")
 	}
-	sf.workingsets.Add(key, ws)
+	sf.putIntoWorkingSets(key, ws)
 	return nil
 }
 
@@ -232,8 +226,8 @@ func (sf *factory) NewBlockBuilder(
 	postSystemActions []action.SealedEnvelope,
 ) (*block.Builder, error) {
 	sf.mutex.Lock()
-	defer sf.mutex.Unlock()
 	ws, err := newWorkingSet(sf.currentChainHeight+1, sf.dao, sf.rootHash(), sf.saveHistory)
+	sf.mutex.Unlock()
 	if err != nil {
 		return nil, errors.Wrap(err, "Failed to obtain working set from state factory")
 	}
@@ -244,7 +238,7 @@ func (sf *factory) NewBlockBuilder(
 
 	blkCtx := protocol.MustGetBlockCtx(ctx)
 	key := generateWorkingSetCacheKey(blkBuilder.GetCurrentBlockHeader(), blkCtx.Producer.String())
-	sf.workingsets.Add(key, ws)
+	sf.putIntoWorkingSets(key, ws)
 	return blkBuilder, nil
 }
 
@@ -269,8 +263,8 @@ func (sf *factory) SimulateExecution(
 // Commit persists all changes in RunActions() into the DB
 func (sf *factory) Commit(ctx context.Context, blk *block.Block) error {
 	sf.mutex.Lock()
-	defer sf.mutex.Unlock()
 	timer := sf.timerFactory.NewTimer("Commit")
+	sf.mutex.Unlock()
 	defer timer.End()
 	producer, err := address.FromBytes(blk.PublicKey().Hash())
 	if err != nil {
@@ -285,24 +279,21 @@ func (sf *factory) Commit(ctx context.Context, blk *block.Block) error {
 			Producer:       producer,
 		},
 	)
-	var ws WorkingSet
 	key := generateWorkingSetCacheKey(blk.Header, blk.Header.ProducerAddress())
-	if data, ok := sf.workingsets.Get(key); ok {
-		if ws, ok = data.(WorkingSet); !ok {
-			return errors.New("type assertion failed to be WorkingSet")
-		}
-	} else {
-		// regenerate the workingset
-		ws, err = newWorkingSet(sf.currentChainHeight+1, sf.dao, sf.rootHash(), sf.saveHistory)
-		if err != nil {
-			return errors.Wrap(err, "Failed to obtain working set from state factory")
-		}
+	ws, isExist, err := sf.getFromWorkingSets(key)
+	if err != nil {
+		return err
+	}
+	if !isExist {
+		// regenerate workingset
 		_, ws, err = runActions(ctx, ws, blk.RunnableActions().Actions())
 		if err != nil {
 			log.L().Panic("Failed to update state.", zap.Error(err))
 			return err
 		}
 	}
+	sf.mutex.Lock()
+	defer sf.mutex.Unlock()
 	if sf.currentChainHeight+1 != ws.Version() {
 		// another working set with correct version already committed, do nothing
 		return fmt.Errorf(
@@ -325,6 +316,9 @@ func (sf *factory) State(addr hash.Hash160, state interface{}, opts ...protocol.
 
 // DeleteWorkingSet returns true if it remove ws from workingsets cache successfully
 func (sf *factory) DeleteWorkingSet(blk *block.Block) error {
+	sf.mutex.RLock()
+	defer sf.mutex.RUnlock()
+
 	key := generateWorkingSetCacheKey(blk.Header, blk.Header.ProducerAddress())
 	sf.workingsets.Remove(key)
 	return nil
@@ -411,7 +405,6 @@ func (sf *factory) commit(ws WorkingSet) error {
 	return nil
 }
 
-// Initialize initializes the state factory
 func (sf *factory) createGenesisStates(ctx context.Context) error {
 	ws, err := newWorkingSet(0, sf.dao, sf.rootHash(), sf.saveHistory)
 	if err != nil {
@@ -426,3 +419,28 @@ func (sf *factory) createGenesisStates(ctx context.Context) error {
 	}
 	return nil
 }
+
+// getFromWorkingSets returns (workingset, true) if it exists in a cache, otherwise generates new workingset and return (ws, false)
+func (sf *factory) getFromWorkingSets(key hash.Hash256) (WorkingSet, bool, error) {
+	sf.mutex.RLock()
+	defer sf.mutex.RUnlock()
+	if data, ok := sf.workingsets.Get(key); ok {
+		if ws, ok := data.(WorkingSet); ok {
+			// if it is already validated, return workingset
+			return ws, true, nil
+		}
+		return nil, false, errors.New("type assertion failed to be WorkingSet")
+	}
+	ws, err := newWorkingSet(sf.currentChainHeight+1, sf.dao, sf.rootHash(), sf.saveHistory)
+	if err != nil {
+		return nil, false, errors.Wrap(err, "failed to obtain working set from state factory")
+	}
+	return ws, false, nil
+}
+
+func (sf *factory) putIntoWorkingSets(key hash.Hash256, ws WorkingSet) {
+	sf.mutex.Lock()
+	defer sf.mutex.Unlock()
+	sf.workingsets.Add(key, ws)
+	return
+}
```

### state/factory/statedb.go
```diff
@@ -159,23 +159,18 @@ func (sdb *stateDB) NewWorkingSet() (WorkingSet, error) {
 }
 
 func (sdb *stateDB) Validate(ctx context.Context, blk *block.Block) error {
-	sdb.mutex.Lock()
-	defer sdb.mutex.Unlock()
 	key := generateWorkingSetCacheKey(blk.Header, blk.Header.ProducerAddress())
-	if data, ok := sdb.workingsets.Get(key); ok {
-		if _, ok := data.(WorkingSet); !ok {
-			return errors.New("type assertion failed to be WorkingSet")
-		}
-		// if already validated, return nil
+	ws, isExist, err := sdb.getFromWorkingSets(key)
+	if err != nil {
+		return err
+	}
+	if isExist {
 		return nil
 	}
-	ws := newStateTX(sdb.currentChainHeight+1, sdb.dao, sdb.saveHistory)
-
-	if err := validateWithWorkingset(ctx, ws, blk); err != nil {
+	if err = validateWithWorkingset(ctx, ws, blk); err != nil {
 		return errors.Wrap(err, "failed to validate block with workingset in statedb")
 	}
-
-	sdb.workingsets.Add(key, ws)
+	sdb.putIntoWorkingSets(key, ws)
 	return nil
 }
 
@@ -186,16 +181,16 @@ func (sdb *stateDB) NewBlockBuilder(
 	postSystemActions []action.SealedEnvelope,
 ) (*block.Builder, error) {
 	sdb.mutex.Lock()
-	defer sdb.mutex.Unlock()
 	ws := newStateTX(sdb.currentChainHeight+1, sdb.dao, sdb.saveHistory)
+	sdb.mutex.Unlock()
 	blkBuilder, err := createBuilderWithWorkingset(ctx, ws, actionMap, postSystemActions, sdb.cfg.Chain.AllowedBlockGasResidue)
 	if err != nil {
 		return nil, err
 	}
 
 	blkCtx := protocol.MustGetBlockCtx(ctx)
 	key := generateWorkingSetCacheKey(blkBuilder.GetCurrentBlockHeader(), blkCtx.Producer.String())
-	sdb.workingsets.Add(key, ws)
+	sdb.putIntoWorkingSets(key, ws)
 	return blkBuilder, nil
 }
 
@@ -217,8 +212,8 @@ func (sdb *stateDB) SimulateExecution(
 // Commit persists all changes in RunActions() into the DB
 func (sdb *stateDB) Commit(ctx context.Context, blk *block.Block) error {
 	sdb.mutex.Lock()
-	defer sdb.mutex.Unlock()
 	timer := sdb.timerFactory.NewTimer("Commit")
+	sdb.mutex.Unlock()
 	defer timer.End()
 	producer, err := address.FromBytes(blk.PublicKey().Hash())
 	if err != nil {
@@ -234,21 +229,19 @@ func (sdb *stateDB) Commit(ctx context.Context, blk *block.Block) error {
 		},
 	)
 	key := generateWorkingSetCacheKey(blk.Header, blk.Header.ProducerAddress())
-	data, ok := sdb.workingsets.Get(key)
-	var ws WorkingSet
-	if ok {
-		if ws, ok = data.(WorkingSet); !ok {
-			return errors.New("type assertion failed to be WorkingSet")
-		}
-	} else {
-		// regenerate the workingset
-		ws = newStateTX(sdb.currentChainHeight+1, sdb.dao, sdb.saveHistory)
+	ws, isExist, err := sdb.getFromWorkingSets(key)
+	if err != nil {
+		return err
+	}
+	if !isExist {
 		_, ws, err = runActions(ctx, ws, blk.RunnableActions().Actions())
 		if err != nil {
 			log.L().Panic("Failed to update state.", zap.Error(err))
 			return err
 		}
 	}
+	sdb.mutex.Lock()
+	defer sdb.mutex.Unlock()
 	if sdb.currentChainHeight+1 != ws.Version() {
 		// another working set with correct version already committed, do nothing
 		return fmt.Errorf(
@@ -281,6 +274,9 @@ func (sdb *stateDB) State(addr hash.Hash160, state interface{}, opts ...protocol
 
 // DeleteWorkingSet returns true if it remove ws from workingsets cache successfully
 func (sdb *stateDB) DeleteWorkingSet(blk *block.Block) error {
+	sdb.mutex.Lock()
+	defer sdb.mutex.Unlock()
+
 	key := generateWorkingSetCacheKey(blk.Header, blk.Header.ProducerAddress())
 	sdb.workingsets.Remove(key)
 	return nil
@@ -323,7 +319,6 @@ func (sdb *stateDB) commit(ws WorkingSet) error {
 	return nil
 }
 
-// Initialize initializes the state db
 func (sdb *stateDB) createGenesisStates(ctx context.Context) error {
 	ws := newStateTX(0, sdb.dao, sdb.saveHistory)
 	if err := createGenesisStates(ctx, ws); err != nil {
@@ -332,3 +327,24 @@ func (sdb *stateDB) createGenesisStates(ctx context.Context) error {
 
 	return sdb.commit(ws)
 }
+
+// getFromWorkingSets returns (workingset, true) if it exists in a cache, otherwise generates new workingset and return (ws, false)
+func (sdb *stateDB) getFromWorkingSets(key hash.Hash256) (WorkingSet, bool, error) {
+	sdb.mutex.RLock()
+	defer sdb.mutex.RUnlock()
+	if data, ok := sdb.workingsets.Get(key); ok {
+		if ws, ok := data.(WorkingSet); ok {
+			// if it is already validated, return workingset
+			return ws, true, nil
+		}
+		return nil, false, errors.New("type assertion failed to be WorkingSet")
+	}
+	return newStateTX(sdb.currentChainHeight+1, sdb.dao, sdb.saveHistory), false, nil
+}
+
+func (sdb *stateDB) putIntoWorkingSets(key hash.Hash256, ws WorkingSet) {
+	sdb.mutex.Lock()
+	defer sdb.mutex.Unlock()
+	sdb.workingsets.Add(key, ws)
+	return
+}
```
