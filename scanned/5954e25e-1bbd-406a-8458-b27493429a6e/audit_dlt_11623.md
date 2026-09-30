# [?] fix(cosmos-vm): prevent some hangs and crashes in `agd` (#11433)

## Summary
Severity: Unknown
Chain: Agoric
Component: Agoric/agoric-sdk
Published: 2025-06-09
Source: https://github.com/Agoric/agoric-sdk/commit/2ad9bd297062a888cf969d741255e18e52c5d60f
Type: security-commit

## Details
fix(cosmos-vm): prevent some hangs and crashes in `agd` (#11433)

closes: #11396, closes: #11395

## Description

- Introduce locks around `vm.ClientCodec` internal state.
- Explicitly `recover()` from Golang panics and propagate errors to the VM controller.

### Security Considerations

Provide better auditability if `agd` crashes.

### Scaling Considerations

Makes the `vm` package correct even with interleaving parallel operations.

### Documentation Considerations

n/a

### Testing Considerations

n/a

### Upgrade Considerations

n/a

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

### golang/cosmos/vm/client.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 	"fmt"
 	"net/rpc"
+	"sync"
 )
 
 // ReceiveMessageMethod is the name of the method we call in order to have the
@@ -34,12 +35,21 @@ var _ rpc.ClientCodec = (*ClientCodec)(nil)
 // having the WriteRequest() method fabricate a Receive() call to clear the rpc
 // state.
 type ClientCodec struct {
-	ctx         context.Context
-	send        func(port, rPort int, msg string)
-	outbound    map[int]rpc.Request
-	inbound     chan *rpc.Response
-	replies     map[uint64]string
+	ctx     context.Context
+	send    func(port, rPort int, msg string)
+	inbound chan *rpc.Response
+
+	// reqMutex protects outbound requests.
+	reqMutex sync.Mutex
+	outbound map[int]rpc.Request
+
+	// Scratch space to communicate between ReadResponseHeader and
+	// ReadResponseBody (protected by mutex in "net/rpc" implementation).
 	replyToRead uint64
+
+	// mutex protects replies map
+	mutex   sync.Mutex
+	replies map[uint64]string
 }
 
 // NewClientCodec creates a new ClientCodec.
@@ -64,7 +74,11 @@ func (cc *ClientCodec) WriteRequest(r *rpc.Request, body interface{}) error {
 		return fmt.Errorf("body %T is not a Message", body)
 	}
 	rPort := int(r.Seq + 1) // rPort is 1-indexed to indicate it's required
+
+	cc.reqMutex.Lock()
 	cc.outbound[rPort] = *r
+	cc.reqMutex.Unlock()
+
 	var senderReplyPort int
 	if msg.NeedsReply {
 		senderReplyPort = rPort
@@ -85,26 +99,37 @@ func (cc *ClientCodec) ReadResponseHeader(r *rpc.Response) error {
 }
 
 // ReadResponseBody decodes a response body (currently just string) from the VM.
+// and will always be called immediately after ReadResponseHeader (cf.
+// https://pkg.go.dev/net/rpc#ClientCodec ).
 func (cc *ClientCodec) ReadResponseBody(body interface{}) error {
+	cc.mutex.Lock()
+	reply := cc.replies[cc.replyToRead]
+	delete(cc.replies, cc.replyToRead)
+	cc.mutex.Unlock()
+
 	if body != nil {
-		*body.(*string) = cc.replies[cc.replyToRead]
+		*body.(*string) = reply
 	}
-	delete(cc.replies, cc.replyToRead)
 	return nil
 }
 
 // Receive is called by the VM to send a response to the client.
 func (cc *ClientCodec) Receive(rPort int, isError bool, data string) error {
+	cc.reqMutex.Lock()
 	outb := cc.outbound[rPort]
 	delete(cc.outbound, rPort)
+	cc.reqMutex.Unlock()
+
 	resp := &rpc.Response{
 		ServiceMethod: outb.ServiceMethod,
 		Seq:           outb.Seq,
 	}
 	if isError {
 		resp.Error = data
 	} else {
+		cc.mutex.Lock()
 		cc.replies[resp.Seq] = data
+		cc.mutex.Unlock()
 	}
 	cc.inbound <- resp
 	return nil
```
