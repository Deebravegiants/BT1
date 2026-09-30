# [?] fix deadlock between monitor service and init-sync (#12427)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2023-05-18
Source: https://github.com/OffchainLabs/prysm/commit/aeaa72fdc2e274e9b2d749f607e41fae18ac77c6
Type: security-commit

## Details
fix deadlock between monitor service and init-sync (#12427)

Co-authored-by: Kasey Kirkham <kasey@users.noreply.github.com>

## Patch
### beacon-chain/monitor/service.go
```diff
@@ -114,19 +114,11 @@ func (s *Service) Start() {
 		"ValidatorIndices": tracked,
 	}).Info("Starting service")
 
-	stateChannel := make(chan *feed.Event, 1)
-	stateSub := s.config.StateNotifier.StateFeed().Subscribe(stateChannel)
-
-	go s.run(stateChannel, stateSub)
+	go s.run()
 }
 
 // run waits until the beacon is synced and starts the monitoring system.
-func (s *Service) run(stateChannel chan *feed.Event, stateSub event.Subscription) {
-	if stateChannel == nil {
-		log.Error("State state is nil")
-		return
-	}
-
+func (s *Service) run() {
 	if err := s.waitForSync(s.config.InitialSyncComplete); err != nil {
 		log.WithError(err)
 		return
@@ -154,6 +146,8 @@ func (s *Service) run(stateChannel chan *feed.Event, stateSub event.Subscription
 	s.isLogging = true
 	s.Unlock()
 
+	stateChannel := make(chan *feed.Event, 1)
+	stateSub := s.config.StateNotifier.StateFeed().Subscribe(stateChannel)
 	s.monitorRoutine(stateChannel, stateSub)
 }
 
```

### beacon-chain/monitor/service_test.go
```diff
@@ -271,11 +271,9 @@ func TestWaitForSyncCanceled(t *testing.T) {
 func TestRun(t *testing.T) {
 	hook := logTest.NewGlobal()
 	s := setupService(t)
-	stateChannel := make(chan *feed.Event, 1)
-	stateSub := s.config.StateNotifier.StateFeed().Subscribe(stateChannel)
 
 	go func() {
-		s.run(stateChannel, stateSub)
+		s.run()
 	}()
 	close(s.config.InitialSyncComplete)
 
```

### testing/endtoend/components/beacon_node.go
```diff
@@ -268,6 +268,8 @@ func (node *BeaconNode) Start(ctx context.Context) error {
 		fmt.Sprintf("--%s=%s", cmdshared.VerbosityFlag.Name, "debug"),
 		fmt.Sprintf("--%s=%d", flags.BlockBatchLimitBurstFactor.Name, 8),
 		fmt.Sprintf("--%s=%s", cmdshared.ChainConfigFileFlag.Name, cfgPath),
+		"--" + cmdshared.ValidatorMonitorIndicesFlag.Name + "=1",
+		"--" + cmdshared.ValidatorMonitorIndicesFlag.Name + "=2",
 		"--" + cmdshared.ForceClearDB.Name,
 		"--" + cmdshared.AcceptTosFlag.Name,
 		"--" + flags.EnableDebugRPCEndpoints.Name,
```
