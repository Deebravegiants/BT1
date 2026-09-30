# [?] go/worker/keymanager: Fix crash on capability TEE updates

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2022-05-03
Source: https://github.com/oasisprotocol/oasis-core/commit/e9726563c4bdfebce80c4b7330549ef5f172ae0a
Type: security-commit

## Details
go/worker/keymanager: Fix crash on capability TEE updates

## Patch
### .changelog/4725.bugfix.md
```diff
@@ -0,0 +1 @@
+go/worker/keymanager: Fix crash on capability TEE updates
```

### go/worker/keymanager/worker.go
```diff
@@ -18,6 +18,7 @@ import (
 	"github.com/oasisprotocol/oasis-core/go/common/node"
 	"github.com/oasisprotocol/oasis-core/go/common/pubsub"
 	"github.com/oasisprotocol/oasis-core/go/common/service"
+	"github.com/oasisprotocol/oasis-core/go/common/version"
 	consensus "github.com/oasisprotocol/oasis-core/go/consensus/api"
 	"github.com/oasisprotocol/oasis-core/go/keymanager/api"
 	registry "github.com/oasisprotocol/oasis-core/go/registry/api"
@@ -47,6 +48,11 @@ var (
 	errMalformedResponse = fmt.Errorf("worker/keymanager: malformed response from worker")
 )
 
+type runtimeStatus struct {
+	version       version.Version
+	capabilityTEE *node.CapabilityTEE
+}
+
 // The key manager worker.
 //
 // It behaves differently from other workers as the key manager has its
@@ -214,7 +220,7 @@ func (w *Worker) CallEnclave(ctx context.Context, data []byte) ([]byte, error) {
 	return resp.Response, nil
 }
 
-func (w *Worker) updateStatus(status *api.Status, startedEvent *host.StartedEvent) error {
+func (w *Worker) updateStatus(status *api.Status, runtimeStatus *runtimeStatus) error {
 	var initOk bool
 	defer func() {
 		if !initOk {
@@ -291,7 +297,7 @@ func (w *Worker) updateStatus(status *api.Status, startedEvent *host.StartedEven
 	}
 
 	// Validate the signature.
-	if tee := startedEvent.CapabilityTEE; tee != nil {
+	if tee := runtimeStatus.capabilityTEE; tee != nil {
 		var signingKey signature.PublicKey
 
 		switch tee.Hardware {
@@ -324,10 +330,10 @@ func (w *Worker) updateStatus(status *api.Status, startedEvent *host.StartedEven
 	// Register as we are now ready to handle requests.
 	initOk = true
 	w.roleProvider.SetAvailableWithCallback(func(n *node.Node) error {
-		rt := n.AddOrUpdateRuntime(w.runtime.ID(), startedEvent.Version)
-		rt.Version = startedEvent.Version
+		rt := n.AddOrUpdateRuntime(w.runtime.ID(), runtimeStatus.version)
+		rt.Version = runtimeStatus.version
 		rt.ExtraInfo = cbor.Marshal(signedInitResp)
-		rt.Capabilities.TEE = startedEvent.CapabilityTEE
+		rt.Capabilities.TEE = runtimeStatus.capabilityTEE
 		return nil
 	}, func(context.Context) error {
 		w.logger.Info("Key manager registered")
@@ -554,9 +560,9 @@ func (w *Worker) worker() { // nolint: gocyclo
 	defer rtSub.Close()
 
 	var (
-		hrtEventCh          <-chan *host.Event
-		currentStatus       *api.Status
-		currentStartedEvent *host.StartedEvent
+		hrtEventCh           <-chan *host.Event
+		currentStatus        *api.Status
+		currentRuntimeStatus *runtimeStatus
 
 		runtimeID = w.runtime.ID()
 	)
@@ -566,7 +572,18 @@ func (w *Worker) worker() { // nolint: gocyclo
 			switch {
 			case ev.Started != nil, ev.Updated != nil:
 				// Runtime has started successfully.
-				currentStartedEvent = ev.Started
+				currentRuntimeStatus = &runtimeStatus{}
+				switch {
+				case ev.Started != nil:
+					currentRuntimeStatus.version = ev.Started.Version
+					currentRuntimeStatus.capabilityTEE = ev.Started.CapabilityTEE
+				case ev.Updated != nil:
+					currentRuntimeStatus.version = ev.Updated.Version
+					currentRuntimeStatus.capabilityTEE = ev.Updated.CapabilityTEE
+				default:
+					continue
+				}
+
 				if currentStatus == nil {
 					continue
 				}
@@ -575,24 +592,24 @@ func (w *Worker) worker() { // nolint: gocyclo
 				// control.
 				if w.enclaveStatus == nil {
 					w.roleProvider.SetAvailable(func(n *node.Node) error {
-						rt := n.AddOrUpdateRuntime(w.runtime.ID(), currentStartedEvent.Version)
-						rt.Version = currentStartedEvent.Version
+						rt := n.AddOrUpdateRuntime(w.runtime.ID(), currentRuntimeStatus.version)
+						rt.Version = currentRuntimeStatus.version
 						rt.ExtraInfo = nil
-						rt.Capabilities.TEE = currentStartedEvent.CapabilityTEE
+						rt.Capabilities.TEE = currentRuntimeStatus.capabilityTEE
 						return nil
 					})
 				}
 
 				// Forward status update to key manager runtime.
-				if err = w.updateStatus(currentStatus, currentStartedEvent); err != nil {
+				if err = w.updateStatus(currentStatus, currentRuntimeStatus); err != nil {
 					w.logger.Error("failed to handle status update",
 						"err", err,
 					)
 					continue
 				}
 			case ev.FailedToStart != nil, ev.Stopped != nil:
 				// Worker failed to start or was stopped -- we can no longer service requests.
-				currentStartedEvent = nil
+				currentRuntimeStatus = nil
 				w.roleProvider.SetUnavailable()
 			default:
 				// Unknown event.
@@ -661,12 +678,12 @@ func (w *Worker) worker() { // nolint: gocyclo
 			}
 
 			currentStatus = status
-			if currentStartedEvent == nil {
+			if currentRuntimeStatus == nil {
 				continue
 			}
 
 			// Forward status update to key manager runtime.
-			if err = w.updateStatus(currentStatus, currentStartedEvent); err != nil {
+			if err = w.updateStatus(currentStatus, currentRuntimeStatus); err != nil {
 				w.logger.Error("failed to handle status update",
 					"err", err,
 				)
@@ -680,10 +697,10 @@ func (w *Worker) worker() { // nolint: gocyclo
 				continue
 			}
 		case <-w.initTickerCh:
-			if currentStatus == nil || currentStartedEvent == nil {
+			if currentStatus == nil || currentRuntimeStatus == nil {
 				continue
 			}
-			if err = w.updateStatus(currentStatus, currentStartedEvent); err != nil {
+			if err = w.updateStatus(currentStatus, currentRuntimeStatus); err != nil {
 				w.logger.Error("failed to handle status update", "err", err)
 				continue
 			}
```
