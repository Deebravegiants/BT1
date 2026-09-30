# [?] op-conductor: Fix deadlock in shutdown (#10728)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-06-04
Source: https://github.com/bobanetwork/boba/commit/e19b3ca274226a76d82e11e23d1e81d22b3beaeb
Type: security-commit

## Details
op-conductor: Fix deadlock in shutdown (#10728)

* op-conductor: Fix deadlock in shutdown

* op-e2e: Unskip test

* Return early

* Remove unnecessary for loop

## Patch
### op-conductor/health/monitor.go
```diff
@@ -117,7 +117,13 @@ func (hm *SequencerHealthMonitor) loop() {
 		case <-ticker.C:
 			err := hm.healthCheck()
 			hm.metrics.RecordHealthCheck(err == nil, err)
-			hm.healthUpdateCh <- err
+			// Ensure that we exit cleanly if told to shutdown while still waiting to publish the health update
+			select {
+			case hm.healthUpdateCh <- err:
+				continue
+			case <-hm.done:
+				return
+			}
 		}
 	}
 }
```

### op-e2e/sequencer_failover_test.go
```diff
@@ -148,7 +148,6 @@ func TestSequencerFailover_ConductorRPC(t *testing.T) {
 // [Category: Sequencer Failover]
 // Test that the sequencer can successfully failover to a new sequencer once the active sequencer goes down.
 func TestSequencerFailover_ActiveSequencerDown(t *testing.T) {
-	t.Skip("Triggers a deadlock in shutdown")
 	sys, conductors, cleanup := setupSequencerFailoverTest(t)
 	defer cleanup()
 
```
