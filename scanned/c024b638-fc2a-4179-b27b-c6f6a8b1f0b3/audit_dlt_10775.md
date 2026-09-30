# [?] go/worker/keymanager: Fix race condition when accessing runtime status

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-01-15
Source: https://github.com/oasisprotocol/oasis-core/commit/c7ae3970df1c6a675b9510d4814fac7fa72e0e1c
Type: security-commit

## Details
go/worker/keymanager: Fix race condition when accessing runtime status

## Patch
### go/worker/keymanager/status.go
```diff
@@ -4,7 +4,6 @@ import (
 	"github.com/libp2p/go-libp2p/core/peer"
 
 	"github.com/oasisprotocol/oasis-core/go/common"
-	"github.com/oasisprotocol/oasis-core/go/common/version"
 	"github.com/oasisprotocol/oasis-core/go/worker/keymanager/api"
 )
 
@@ -61,15 +60,10 @@ func (w *Worker) GetStatus() (*api.Status, error) {
 		pc = w.enclaveStatus.InitResponse.PolicyChecksum
 	}
 
-	var aw *version.Version
-	if w.rtStatus != nil {
-		aw = &w.rtStatus.version
-	}
-
 	gs := w.globalStatus
 	ws := api.WorkerStatus{
 		Status:           ss,
-		ActiveVersion:    aw,
+		ActiveVersion:    w.activeVersion,
 		MayGenerate:      w.mayGenerate,
 		RuntimeID:        &w.runtimeID,
 		ClientRuntimes:   rts,
```

### go/worker/keymanager/worker.go
```diff
@@ -94,6 +94,7 @@ type Worker struct { // nolint: maligned
 	globalStatus  *api.Status
 	enclaveStatus *api.SignedInitResponse
 	policy        *api.SignedPolicySGX
+	activeVersion *version.Version
 
 	masterSecretStats    workerKeymanager.MasterSecretStats
 	ephemeralSecretStats workerKeymanager.EphemeralSecretStats
@@ -408,6 +409,13 @@ func (w *Worker) setStatus(status *api.Status) {
 	w.globalStatus = status
 }
 
+func (w *Worker) setVersion(v *version.Version) {
+	w.Lock()
+	defer w.Unlock()
+
+	w.activeVersion = v
+}
+
 func (w *Worker) setLastGeneratedMasterSecretGeneration(generation uint64) {
 	w.Lock()
 	defer w.Unlock()
@@ -1029,6 +1037,7 @@ func (w *Worker) handleRuntimeHostEvent(ev *host.Event) {
 		default:
 			return
 		}
+		w.setVersion(&w.rtStatus.version)
 
 		if w.kmStatus == nil {
 			return
@@ -1055,6 +1064,7 @@ func (w *Worker) handleRuntimeHostEvent(ev *host.Event) {
 	case ev.FailedToStart != nil, ev.Stopped != nil:
 		// Worker failed to start or was stopped -- we can no longer service requests.
 		w.rtStatus = nil
+		w.setVersion(nil)
 		w.roleProvider.SetUnavailable()
 	default:
 		// Unknown event.
```
