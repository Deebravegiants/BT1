# [?] Fix panic issues on beacon node shutdown (#7625)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2020-10-23
Source: https://github.com/OffchainLabs/prysm/commit/7e2112b4bad166a3194cd368ececb2b902462423
Type: security-commit

## Details
Fix panic issues on beacon node shutdown (#7625)

* allow service cleanup on node shutdown

* revert error to fatal

* remove unused struct field

## Patch
### beacon-chain/node/node.go
```diff
@@ -62,7 +62,6 @@ const testSkipPowFlag = "test-skip-pow"
 type BeaconNode struct {
 	cliCtx            *cli.Context
 	ctx               context.Context
-	cancel            context.CancelFunc
 	services          *shared.ServiceRegistry
 	lock              sync.RWMutex
 	stop              chan struct{} // Channel to wait for termination notifications.
@@ -155,11 +154,9 @@ func NewBeaconNode(cliCtx *cli.Context) (*BeaconNode, error) {
 
 	registry := shared.NewServiceRegistry()
 
-	ctx, cancel := context.WithCancel(cliCtx.Context)
 	beacon := &BeaconNode{
 		cliCtx:            cliCtx,
-		ctx:               ctx,
-		cancel:            cancel,
+		ctx:               cliCtx.Context,
 		services:          registry,
 		stop:              make(chan struct{}),
 		stateFeed:         new(event.Feed),
@@ -279,7 +276,6 @@ func (b *BeaconNode) Close() {
 	defer b.lock.Unlock()
 
 	log.Info("Stopping beacon node")
-	b.cancel() // Cancel the beacon node struct's context.
 	b.services.StopAll()
 	if err := b.db.Close(); err != nil {
 		log.Errorf("Failed to close database: %v", err)
@@ -306,7 +302,7 @@ func (b *BeaconNode) startDB(cliCtx *cli.Context) error {
 	}
 	clearDBConfirmed := false
 	if clearDB && !forceClearDB {
-		actionText := "This will delete your beacon chain data base stored in your data directory. " +
+		actionText := "This will delete your beacon chain database stored in your data directory. " +
 			"Your database backups will not be removed - do you want to proceed? (Y/N)"
 		deniedText := "Database will not be deleted. No changes have been made."
 		clearDBConfirmed, err = cmd.ConfirmAction(actionText, deniedText)
```

### beacon-chain/sync/initial-sync/service.go
```diff
@@ -109,6 +109,9 @@ func (s *Service) Start() {
 	}
 	s.waitForMinimumPeers()
 	if err := s.roundRobinSync(genesis); err != nil {
+		if errors.Is(s.ctx.Err(), context.Canceled) {
+			return
+		}
 		panic(err)
 	}
 	log.Infof("Synced up to slot %d", s.chain.HeadSlot())
```
