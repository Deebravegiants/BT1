# [?] Merge pull request #9962 from yyforyongyu/fix-panic

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-06-18
Source: https://github.com/lightningnetwork/lnd/commit/31c74f20fa46259dcd351ba277a9a216fc6edcdc
Type: security-commit

## Details
Merge pull request #9962 from yyforyongyu/fix-panic

chainio: use package logger instead of instance logger

## Patch
### chainio/dispatcher.go
```diff
@@ -135,6 +135,14 @@ func (b *BlockbeatDispatcher) Stop() {
 }
 
 func (b *BlockbeatDispatcher) log() btclog.Logger {
+	// There's no guarantee that the `b.beat` is initialized when the
+	// dispatcher shuts down, especially in the case where the node is
+	// running as a remote signer, which doesn't have a chainbackend. In
+	// that case we will use the package logger.
+	if b.beat == nil {
+		return clog
+	}
+
 	return b.beat.logger()
 }
 
```

### docs/release-notes/release-notes-0.19.2.md
```diff
@@ -26,6 +26,9 @@
 - [Fixed](https://github.com/lightningnetwork/lnd/pull/9921) a case where the
   spending notification of an output may be missed if wrong height hint is used.
 
+- [Fixed](https://github.com/lightningnetwork/lnd/pull/9962) a case where the
+  node may panic if it's running in the remote signer mode.
+
 # New Features
 
 ## Functional Enhancements
```
