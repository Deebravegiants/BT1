# [?] go/oasis-test-runner: Fix crash during node restart

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-05-25
Source: https://github.com/oasisprotocol/oasis-core/commit/175eb228b3551a253bb77f086c6faa84ae2a153c
Type: security-commit

## Details
go/oasis-test-runner: Fix crash during node restart

## Patch
### go/oasis-test-runner/oasis/args.go
```diff
@@ -60,6 +60,16 @@ type argBuilder struct {
 	dontBlameOasis bool
 }
 
+func (args *argBuilder) clone() *argBuilder {
+	vec := make([]Argument, len(args.vec))
+	copy(vec[:], args.vec)
+
+	return &argBuilder{
+		vec:            vec,
+		dontBlameOasis: args.dontBlameOasis,
+	}
+}
+
 func (args *argBuilder) internalSocketAddress(path string) *argBuilder {
 	args.vec = append(args.vec, Argument{
 		Name:   grpc.CfgAddress,
```

### go/oasis-test-runner/oasis/network.go
```diff
@@ -590,6 +590,9 @@ func (net *Network) startOasisNode(
 	node.Lock()
 	defer node.Unlock()
 
+	// Make a deep copy as we will be modifying the arguments.
+	initialExtraArgs := extraArgs.clone()
+
 	baseArgs := []string{
 		"--" + cmdCommon.CfgDataDir, node.dir.String(),
 		"--log.level", "debug",
@@ -667,7 +670,7 @@ func (net *Network) startOasisNode(
 			if errors.As(err, &exitErr) && exitErr.ExitCode() == crash.CrashDefaultExitCode {
 				// Termination due to crasher. Restart node.
 				net.logger.Info("Node debug crash point triggered. Restarting...", "node", node.Name)
-				if err = net.startOasisNode(node, subCmd, extraArgs); err != nil {
+				if err = net.startOasisNode(node, subCmd, initialExtraArgs); err != nil {
 					net.errCh <- fmt.Errorf("oasis: %s failed restarting node after crash point: %w", node.Name, err)
 				}
 				return
```
