# [?] go/worker/registration: Fix crash when failing to query sentry addresses

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-04-07
Source: https://github.com/oasisprotocol/oasis-core/commit/2947898eabf48a0f3281466fa08f64bce2ae1154
Type: security-commit

## Details
go/worker/registration: Fix crash when failing to query sentry addresses

## Patch
### .changelog/2825.bugfix.md
```diff
@@ -0,0 +1 @@
+go/worker/registration: Fix crash when failing to query sentry addresses
```

### go/worker/registration/worker.go
```diff
@@ -686,6 +686,7 @@ func (w *Worker) querySentries() ([]node.ConsensusAddress, []node.CommitteeAddre
 				"err", err,
 				"sentry_address", sentryAddr,
 			)
+			continue
 		}
 
 		// Keep sentries updated with our latest TLS certificates.
```
