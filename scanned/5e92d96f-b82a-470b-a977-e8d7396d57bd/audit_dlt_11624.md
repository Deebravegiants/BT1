# [?] fix(libdaemon): handle panics in `//export` functions`

## Summary
Severity: Unknown
Chain: Agoric
Component: Agoric/agoric-sdk
Published: 2025-05-30
Source: https://github.com/Agoric/agoric-sdk/commit/22d8d3feb9f7bf09a31f5ed3c6999642726609a6
Type: security-commit

## Details
fix(libdaemon): handle panics in `//export` functions`

## Patch
### golang/cosmos/cmd/libdaemon/main.go
```diff
@@ -15,6 +15,7 @@ import (
 	"net/rpc"
 	"os"
 	"path/filepath"
+	"runtime/debug"
 
 	log "github.com/cometbft/cometbft/libs/log"
 
@@ -25,13 +26,20 @@ import (
 	servertypes "github.com/cosmos/cosmos-sdk/server/types"
 )
 
+// Taken from sysexits.h
+const (
+	EX_SOFTWARE = 70 /* internal software error */
+)
+
 type goReturn = struct {
 	str string
 	err error
 }
 
 const SwingSetPort = 123
 
+var logger = log.NewTMLogger(log.NewSyncWriter(os.Stderr)).With("module", "cmd/libdaemon")
+
 var vmClientCodec *vm.ClientCodec
 var agdServer *vm.AgdServer
 
@@ -59,8 +67,29 @@ func ConnectVMClientCodec(ctx context.Context, nodePort int, sendFunc func(int,
 	return vmClientCodec, sendToNode
 }
 
+// handlePanic is a helper function to recover from panics, log them, and exit the process.
+func handlePanic(caller string) {
+	if r := recover(); r != nil {
+		defer func() {
+			if err := recover(); err != nil {
+				// If we panic again, we will exit the process without logging the error or stack.
+				os.Stderr.WriteString("Double panic in exported Go function: " + caller + "\n")
+				os.Exit(EX_SOFTWARE)
+			}
+		}()
+
+		// Log the panic with the caller information.
+		logger.Error("Panic in exported Go function", "caller", caller, "error", r, "stack", debug.Stack())
+
+		// Exit the process with a non-zero exit code.
+		os.Exit(EX_SOFTWARE)
+	}
+}
+
 //export RunAgCosmosDaemon
 func RunAgCosmosDaemon(nodePort C.int, toNode C.sendFunc, cosmosArgs []*C.char) C.int {
+	defer handlePanic("RunAgCosmosDaemon")
+
 	userHomeDir, err := os.UserHomeDir()
 	if err != nil {
 		panic(err)
@@ -92,6 +121,8 @@ func RunAgCosmosDaemon(nodePort C.int, toNode C.sendFunc, cosmosArgs []*C.char)
 	// fmt.Fprintln(os.Stderr, "Starting Cosmos", args)
 	os.Args = args
 	go func() {
+		defer handlePanic("daemon.RunWithController")
+
 		// We run in the background, but exit when the job is over.
 		// swingset.SendToNode("hello from Initial Go!")
 		exitCode := 0
@@ -112,6 +143,7 @@ func RunAgCosmosDaemon(nodePort C.int, toNode C.sendFunc, cosmosArgs []*C.char)
 
 //export ReplyToGo
 func ReplyToGo(replyPort C.int, isError C.int, resp C.Body) C.int {
+	defer handlePanic("ReplyToGo")
 	respStr := C.GoString(resp)
 	// fmt.Printf("Reply to Go %d %s\n", replyPort, respStr)
 	if err := vmClientCodec.Receive(int(replyPort), int(isError) != 0, respStr); err != nil {
@@ -126,6 +158,7 @@ type errorWrapper struct {
 
 //export SendToGo
 func SendToGo(port C.int, msg C.Body) C.Body {
+	defer handlePanic("SendToGo")
 	msgStr := C.GoString(msg)
 	// fmt.Fprintln(os.Stderr, "Send to Go", msgStr)
 	var respStr string
```
