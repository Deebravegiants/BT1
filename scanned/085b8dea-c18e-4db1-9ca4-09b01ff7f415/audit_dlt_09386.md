# [?] fix(sync): Panic on shutdown (#279)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-02-24
Source: https://github.com/berachain/beacon-kit/commit/5ff7a1229210738c206392ecfdd0826c252b6b0f
Type: security-commit

## Details
fix(sync): Panic on shutdown (#279)

* bet

* upgrade

* godoc

* godoc

* godoc

* godoc

* godoc

* nosec

## Patch
### beacon/execution/notify.go
```diff
@@ -32,11 +32,11 @@ import (
 
 	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/ethereum/go-ethereum/common"
+	"github.com/itsdevbear/bolaris/config/version"
 	eth "github.com/itsdevbear/bolaris/engine/ethclient"
 	enginetypes "github.com/itsdevbear/bolaris/engine/types"
 	enginev1 "github.com/itsdevbear/bolaris/engine/types/v1"
 	"github.com/itsdevbear/bolaris/types/consensus/primitives"
-	"github.com/itsdevbear/bolaris/types/consensus/version"
 )
 
 // notifyNewPayload notifies the execution client of a new payload.
```

### beacon/sync/beacon.go
```diff
@@ -40,7 +40,6 @@ func (s *Service) CheckCLSync(ctx context.Context) error {
 	// Exit early if the node does not return a progress.
 	// This means the node is in sync at the eth1 layer.
 	if !resultStatus.SyncInfo.CatchingUp {
-		s.Logger().Info("beacon client is synchronized to head.")
 		return nil
 	}
 
```

### beacon/sync/errors.go
```diff
@@ -28,10 +28,18 @@ package sync
 import "errors"
 
 var (
+	// ErrConsensusClientIsSyncing indicates that the consensus client
+	// is still in the process of syncing.
 	ErrConsensusClientIsSyncing = errors.New(
 		"consensus client is still syncing",
 	)
+	// ErrExecutionClientIsSyncing indicates that the execution client
+	// is still in the process of syncing.
 	ErrExecutionClientIsSyncing = errors.New(
 		"execution client is still syncing",
 	)
+	// ErrNotRunning indicates that the service is not currently running.
+	ErrNotRunning = errors.New(
+		"service is not running",
+	)
 )
```

### beacon/sync/execution.go
```diff
@@ -40,7 +40,6 @@ func (s *Service) CheckELSync(ctx context.Context) error {
 	// Exit early if the node does not return a progress.
 	// This means the node is in sync at the eth1 layer.
 	if progress == nil {
-		s.Logger().Info("execution client is synchronized eth1 head.")
 		return nil
 	}
 
```

### beacon/sync/service.go
```diff
@@ -27,8 +27,7 @@ package sync
 
 import (
 	"context"
-	"errors"
-	"sync/atomic"
+	"sync"
 	"time"
 
 	"github.com/cosmos/cosmos-sdk/client"
@@ -37,63 +36,70 @@ import (
 	"golang.org/x/sync/errgroup"
 )
 
+// syncLoopInterval is the interval at which the sync loop checks for sync
+// status.
+//
+
+const syncLoopInterval = 6 * time.Second
+
 // Service is responsible for tracking the synchornization status
 // of both the beacon and execution chains.
 type Service struct {
 	service.BaseService
-	ethClient        *eth.Eth1Client
-	clientCtx        *client.Context
-	notifySyncSignal chan struct{}
-	synced           atomic.Bool
+	ethClient *eth.Eth1Client
+	clientCtx *client.Context
+
+	// statusErrMu protects statusErr.
+	statusErrMu sync.Mutex
+	// statusErr is the error returned
+	// by the last status check.
+	statusErr error
 }
 
+// Status checks if the service is currently synced.
 func (s *Service) Status() error {
-	if !s.synced.Load() {
-		return errors.New("fallen out of sync")
-	}
-	return nil
+	s.statusErrMu.Lock()
+	defer s.statusErrMu.Unlock()
+	return s.statusErr
 }
 
+// SetClientContext sets the client context for the service.
 func (s *Service) SetClientContext(clientCtx client.Context) {
 	s.clientCtx = &clientCtx
 }
 
+// Start initiates the synchronization service.
 func (s *Service) Start(ctx context.Context) {
-	s.notifySyncSignal = make(chan struct{})
-
+	// Start the synchronization loop in a new goroutine.
 	go func() {
-		err := s.syncLoop(ctx)
-		if err != nil {
-			panic("sync state is bad")
-		}
+		// Call syncLoop to continuously check and update the sync status.
+		s.syncLoop(ctx)
+		// Once the context is done, close
+		// the notifySyncSignal channel to signal completion.
 		<-ctx.Done()
-		close(s.notifySyncSignal)
 	}()
 }
 
 // syncLoop continuously runs and reports if our client is out of sync.
-func (s *Service) syncLoop(ctx context.Context) error {
-	var err error
-	ticker := time.NewTicker(1 * time.Second)
+func (s *Service) syncLoop(ctx context.Context) {
+	ticker := time.NewTicker(syncLoopInterval)
 	defer ticker.Stop()
 
 	for {
 		select {
 		case <-ctx.Done():
-			s.synced.Store(false)
-			return ctx.Err()
+			s.statusErr = ErrNotRunning
+			return
 		case <-ticker.C:
-			err = s.RequestSyncProgress(ctx)
-		}
-
-		if err == nil {
-			s.synced.Store(true)
-		} else {
-			s.synced.Store(false)
+			s.statusErrMu.Lock()
+			//#nosec:G703
+			s.statusErr = s.RequestSyncProgress(ctx)
+			s.statusErrMu.Unlock()
 		}
 	}
 }
 
+// Request the sync progress from the consensus and execution clients.
 func (s *Service) RequestSyncProgress(ctx context.Context) error {
 	g, ctx := errgroup.WithContext(ctx)
 
```

### config/beacon.go
```diff
@@ -26,9 +26,9 @@
 package config
 
 import (
+	"github.com/itsdevbear/bolaris/config/version"
 	"github.com/itsdevbear/bolaris/io/cli/parser"
 	"github.com/itsdevbear/bolaris/types/consensus/primitives"
-	"github.com/itsdevbear/bolaris/types/consensus/version"
 )
 
 // Beacon conforms to the BeaconKitConfig interface.
```

### engine/client.go
```diff
@@ -33,11 +33,11 @@ import (
 	"cosmossdk.io/log"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/itsdevbear/bolaris/config"
+	"github.com/itsdevbear/bolaris/config/version"
 	eth "github.com/itsdevbear/bolaris/engine/ethclient"
 	enginetypes "github.com/itsdevbear/bolaris/engine/types"
 	enginev1 "github.com/itsdevbear/bolaris/engine/types/v1"
 	"github.com/itsdevbear/bolaris/types/consensus/primitives"
-	"github.com/itsdevbear/bolaris/types/consensus/version"
 )
 
 // Caller is implemented by engineClient.
```

### engine/types/factory.go
```diff
@@ -28,8 +28,8 @@ package enginetypes
 import (
 	"errors"
 
+	"github.com/itsdevbear/bolaris/config/version"
 	enginev1 "github.com/itsdevbear/bolaris/engine/types/v1"
-	"github.com/itsdevbear/bolaris/types/consensus/version"
 )
 
 // NewPayloadAttributesContainer creates a new PayloadAttributesContainer.
```

### engine/types/v1/payload_attributes_container.go
```diff
@@ -26,7 +26,7 @@
 package enginev1
 
 import (
-	"github.com/itsdevbear/bolaris/types/consensus/version"
+	"github.com/itsdevbear/bolaris/config/version"
 	"google.golang.org/protobuf/proto"
 )
 
```

### engine/types/v1/payload_container.go
```diff
@@ -26,10 +26,10 @@
 package enginev1
 
 import (
+	"github.com/itsdevbear/bolaris/config/version"
 	"github.com/itsdevbear/bolaris/crypto/sha256"
 	byteslib "github.com/itsdevbear/bolaris/lib/bytes"
 	"github.com/itsdevbear/bolaris/math"
-	"github.com/itsdevbear/bolaris/types/consensus/version"
 	fssz "github.com/prysmaticlabs/fastssz"
 	"google.golang.org/protobuf/proto"
 )
```

### types/consensus/blocks.go
```diff
@@ -26,10 +26,10 @@
 package consensus
 
 import (
+	"github.com/itsdevbear/bolaris/config/version"
 	enginetypes "github.com/itsdevbear/bolaris/engine/types"
 	"github.com/itsdevbear/bolaris/types/consensus/primitives"
 	consensusv1 "github.com/itsdevbear/bolaris/types/consensus/v1"
-	"github.com/itsdevbear/bolaris/types/consensus/version"
 )
 
 // BeaconKitBlock assembles a new beacon block from
```
