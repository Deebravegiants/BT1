# [?] internal/build: fix crash in MustRunCommandWithOutput (#28709)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-12-20
Source: https://github.com/ethereum/go-ethereum/commit/7124057bad16694d2b1f15dfe68a6109961b34ab
Type: security-commit

## Details
internal/build: fix crash in MustRunCommandWithOutput (#28709)

## Patch
### internal/build/util.go
```diff
@@ -68,23 +68,18 @@ func MustRunCommand(cmd string, args ...string) {
 	MustRun(exec.Command(cmd, args...))
 }
 
+// MustRunCommandWithOutput runs the given command, and ensures that some output will be
+// printed while it runs. This is useful for CI builds where the process will be stopped
+// when there is no output.
 func MustRunCommandWithOutput(cmd string, args ...string) {
-	var done chan bool
-	// This is a little loop to generate some output, so CI does not tear down the
-	// process after 300 seconds.
+	interval := time.NewTicker(time.Minute)
+	defer interval.Stop()
 	go func() {
-		for i := 0; i < 15; i++ {
+		for range interval.C {
 			fmt.Printf("Waiting for command %q\n", cmd)
-			select {
-			case <-time.After(time.Minute):
-				break
-			case <-done:
-				return
-			}
 		}
 	}()
 	MustRun(exec.Command(cmd, args...))
-	close(done)
 }
 
 var warnedAboutGit bool
```
