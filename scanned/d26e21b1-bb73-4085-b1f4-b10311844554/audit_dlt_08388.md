# [?] fix(cosmovisor): Fix consensus failure lottery (#24262)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-04-03
Source: https://github.com/cosmos/cosmos-sdk/commit/877b4fb2dcc2a87a775d0f9e760c0e7388c624c5
Type: security-commit

## Details
fix(cosmovisor): Fix consensus failure lottery (#24262)

Co-authored-by: Alex | Interchain Labs <alex@interchainlabs.io>
Co-authored-by: Zygimantas <zygis@skip.build>

## Patch
### tools/cosmovisor/CHANGELOG.md
```diff
@@ -40,6 +40,10 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 * [#23720](https://github.com/cosmos/cosmos-sdk/pull/23720) Get block height from db after node execution fails
 
+### Bug Fixes
+
+* [#23683](https://github.com/cosmos/cosmos-sdk/pull/23683) Replace `SigInt` with `SigTerm` to gracefully shutdown the process.
+
 ## v1.7.1 - 2025-01-12
 
 ### Bug Fixes
```

### tools/cosmovisor/process.go
```diff
@@ -283,7 +283,7 @@ func (l Launcher) WaitForUpgradeOrExit(cmd *exec.Cmd) (bool, error) {
 		if l.cfg.ShutdownGrace > 0 {
 			// Interrupt signal
 			l.logger.Info("sent interrupt to app, waiting for exit")
-			_ = cmd.Process.Signal(os.Interrupt)
+			_ = cmd.Process.Signal(syscall.SIGTERM)
 
 			// Wait app exit
 			psChan := make(chan *os.ProcessState)
```

### tools/cosmovisor/testdata/dontdie/cosmovisor/genesis/bin/dummyd
```diff
@@ -5,7 +5,7 @@ warn() {
     echo "WARN Need Flush"
 }
 
-trap warn INT
+trap warn TERM
 echo Genesis $@
 sleep 1
 test -z $4 && exit 1001
```
