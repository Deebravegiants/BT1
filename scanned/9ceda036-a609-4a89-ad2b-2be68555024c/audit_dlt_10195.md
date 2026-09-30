# [?] Merge pull request #4647 from oasisprotocol/kostko/fix/multihost-stop-deadlock

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2022-04-07
Source: https://github.com/oasisprotocol/oasis-core/commit/202c8b8f8368afa38884384b57854fee6803dbac
Type: security-commit

## Details
Merge pull request #4647 from oasisprotocol/kostko/fix/multihost-stop-deadlock

go/runtime/host: Always emit StoppedEvent on stop

## Patch
### .changelog/4647.bugfix.md
```diff
@@ -0,0 +1,5 @@
+go/runtime/host: Always emit StoppedEvent on stop
+
+Previously the StoppedEvent was only emitted in case the runtime was
+previously running. In case multihost was performing a version switch when a
+runtime was not yet started, this resulted in a deadlock.
```

### go/runtime/host/sandbox/sandbox.go
```diff
@@ -437,11 +437,11 @@ func (r *sandboxedRuntime) manager() {
 			r.Lock()
 			r.conn = nil
 			r.Unlock()
-
-			// Notify subscribers that the runtime has stopped.
-			r.notifier.Broadcast(&host.Event{Stopped: &host.StoppedEvent{}})
 		}
 
+		// Notify subscribers that the runtime has stopped.
+		r.notifier.Broadcast(&host.Event{Stopped: &host.StoppedEvent{}})
+
 		close(r.quitCh)
 	}()
 
```
