# [?] go/worker/keymanager: Fix race condition when accessing enclave status

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-01-16
Source: https://github.com/oasisprotocol/oasis-core/commit/135bd82b4154b0a8a7afe579a88b2074c6524eba
Type: security-commit

## Details
go/worker/keymanager: Fix race condition when accessing enclave status

## Patch
### .changelog/5529.bugfix.md
```diff
@@ -0,0 +1 @@
+go/worker/keymanager: Fix race conditions when accessing status fields
```

### go/worker/keymanager/status.go
```diff
@@ -55,11 +55,6 @@ func (w *Worker) GetStatus() (*api.Status, error) {
 		al = append(al, ral)
 	}
 
-	var pc []byte
-	if w.enclaveStatus != nil {
-		pc = w.enclaveStatus.InitResponse.PolicyChecksum
-	}
-
 	gs := w.globalStatus
 	ws := api.WorkerStatus{
 		Status:           ss,
@@ -70,7 +65,7 @@ func (w *Worker) GetStatus() (*api.Status, error) {
 		AccessList:       al,
 		PrivatePeers:     ps,
 		Policy:           w.policy,
-		PolicyChecksum:   pc,
+		PolicyChecksum:   w.policyChecksum,
 		MasterSecrets:    w.masterSecretStats,
 		EphemeralSecrets: w.ephemeralSecretStats,
 	}
```

### go/worker/keymanager/worker.go
```diff
@@ -91,10 +91,10 @@ type Worker struct { // nolint: maligned
 	roleProvider registration.RoleProvider
 	backend      api.Backend
 
-	globalStatus  *api.Status
-	enclaveStatus *api.SignedInitResponse
-	policy        *api.SignedPolicySGX
-	activeVersion *version.Version
+	globalStatus   *api.Status
+	policy         *api.SignedPolicySGX
+	policyChecksum []byte
+	activeVersion  *version.Version
 
 	masterSecretStats    workerKeymanager.MasterSecretStats
 	ephemeralSecretStats workerKeymanager.EphemeralSecretStats
@@ -358,13 +358,13 @@ func (w *Worker) initEnclave(kmStatus *api.Status, rtStatus *runtimeStatus) (*ap
 
 	// Update metrics.
 	enclaveMasterSecretGenerationNumber.WithLabelValues(w.runtimeLabel).Set(float64(kmStatus.Generation))
-	if w.enclaveStatus == nil || !bytes.Equal(w.enclaveStatus.InitResponse.PolicyChecksum, signedInitResp.InitResponse.PolicyChecksum) {
+	if !bytes.Equal(w.policyChecksum, signedInitResp.InitResponse.PolicyChecksum) {
 		policyUpdateCount.WithLabelValues(w.runtimeLabel).Inc()
 	}
 
-	// Cache the key manager enclave status and the currently active policy.
-	w.enclaveStatus = &signedInitResp
+	// Cache the currently active policy and its checksum.
 	w.policy = kmStatus.Policy
+	w.policyChecksum = signedInitResp.InitResponse.PolicyChecksum
 
 	return &signedInitResp, nil
 }
@@ -1043,10 +1043,16 @@ func (w *Worker) handleRuntimeHostEvent(ev *host.Event) {
 			return
 		}
 
+		// Check whether the enclave has been initialized at least once.
+		// If true, preregistration is not required.
+		w.RLock()
+		initialized := w.policyChecksum != nil
+		w.RUnlock()
+
 		// Send a node preregistration, so that other nodes know to update their access
 		// control. Without it, the enclave won't be able to replicate the master secrets
 		// needed for initialization.
-		if w.enclaveStatus == nil {
+		if !initialized {
 			rtStatus := w.rtStatus
 			w.roleProvider.SetAvailableWithCallback(func(n *node.Node) error {
 				rt := n.AddOrUpdateRuntime(w.runtime.ID(), rtStatus.version)
```
