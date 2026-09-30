# [?] go/runtime: Fix nil pointer dereference in HostRegisterNotify handler

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-07-15
Source: https://github.com/oasisprotocol/oasis-core/commit/bf911d736a01edf60456269a8fad1ad835d82f38
Type: security-commit

## Details
go/runtime: Fix nil pointer dereference in HostRegisterNotify handler

## Patch
### go/runtime/registry/handler_rofl.go
```diff
@@ -260,7 +260,9 @@ func (rh *roflHostHandler) handleHostRegisterNotify(
 	// Subscribe to event notifications.
 	nfs := &rofl.Notifications{
 		Blocks: rq.RuntimeBlock,
-		Events: rq.RuntimeEvent.Tags,
+	}
+	if rq.RuntimeEvent != nil {
+		nfs.Events = rq.RuntimeEvent.Tags
 	}
 	rh.roflNotifier.register(rh.id, nfs)
 
```
