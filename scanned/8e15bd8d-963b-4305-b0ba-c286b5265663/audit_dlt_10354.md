# [?] fix blockProcWg stopping deadlock

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-03-11
Source: https://github.com/0xsoniclabs/sonic/commit/d0ace198cb01671857b36b039ff1df70a576d5b2
Type: security-commit

## Details
fix blockProcWg stopping deadlock

## Patch
### gossip/service.go
```diff
@@ -131,9 +131,10 @@ type Service struct {
 	// version watcher
 	verWatcher *verwatcher.VerWarcher
 
-	blockProcWg      sync.WaitGroup
-	blockProcTasks   *workers.Workers
-	blockProcModules BlockProc
+	blockProcWg        sync.WaitGroup
+	blockProcTasks     *workers.Workers
+	blockProcTasksDone chan struct{}
+	blockProcModules   BlockProc
 
 	blockBusyFlag uint32
 	eventBusyFlag uint32
@@ -175,19 +176,20 @@ func NewService(stack *node.Node, config Config, store *Store, signer valkeystor
 
 func newService(config Config, store *Store, signer valkeystore.SignerI, blockProc BlockProc, engine lachesis.Consensus, dagIndexer *vecmt.Index) (*Service, error) {
 	svc := &Service{
-		config:           config,
-		done:             make(chan struct{}),
-		Name:             fmt.Sprintf("Node-%d", rand.Int()),
-		store:            store,
-		engine:           engine,
-		blockProcModules: blockProc,
-		dagIndexer:       dagIndexer,
-		engineMu:         new(sync.RWMutex),
-		uniqueEventIDs:   uniqueID{new(big.Int)},
-		Instance:         logger.MakeInstance(),
+		config:             config,
+		done:               make(chan struct{}),
+		blockProcTasksDone: make(chan struct{}),
+		Name:               fmt.Sprintf("Node-%d", rand.Int()),
+		store:              store,
+		engine:             engine,
+		blockProcModules:   blockProc,
+		dagIndexer:         dagIndexer,
+		engineMu:           new(sync.RWMutex),
+		uniqueEventIDs:     uniqueID{new(big.Int)},
+		Instance:           logger.MakeInstance(),
 	}
 
-	svc.blockProcTasks = workers.New(&svc.wg, svc.done, 1)
+	svc.blockProcTasks = workers.New(new(sync.WaitGroup), svc.blockProcTasksDone, 1)
 
 	// create server pool
 	trustedNodes := []string{}
@@ -372,6 +374,7 @@ func (s *Service) Stop() error {
 	s.stopped = true
 
 	s.blockProcWg.Wait()
+	close(s.blockProcTasksDone)
 	return s.store.Commit()
 }
 
```
