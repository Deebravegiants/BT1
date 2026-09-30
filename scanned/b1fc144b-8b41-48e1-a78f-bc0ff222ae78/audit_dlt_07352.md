# [?] [FAB-14944] Fix Data race in TestSend

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-04-07
Source: https://github.com/hyperledger/fabric/commit/d1bf8c3b46eb7f153b030d97b0f228fafaa108cb
Type: security-commit

## Details
[FAB-14944] Fix Data race in TestSend

The test has a data race because it re-programs a mock in
a non memory coherent (and wishful thinking) way, and the
goroutine that sends the messages isn't effected by
the mock synchronization attempts in the test, because
they happen after the data race occurs.

This change set fixes the data race by programming the stream's
mock only once, and having it dynamically read the returned values
while holding a lock, which synchronizes between the goroutine
that sends down the stream and the test goroutine.

Ran this 10,000 times with data race detector and it doesn't
fail now.

Change-Id: I8a0030586da9102e8539c9f7b8699c63c6565894
Signed-off-by: yacovm <yacovm@il.ibm.com>

## Patch
### orderer/common/cluster/rpc_test.go
```diff
@@ -10,6 +10,7 @@ import (
 	"context"
 	"io"
 	"sync"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -111,25 +112,6 @@ func TestSend(t *testing.T) {
 		},
 	}
 
-	comm := &mocks.Communicator{}
-	stream := &mocks.StepClient{}
-	client := &mocks.ClusterClient{}
-
-	resetMocks := func() {
-		// When a mock invokes a method from a different goroutine,
-		// it records this invocation. However - we overwrite the recording
-		// in this function.
-
-		// Call a setter method on the mock, so it will
-		// lock itself and thus synchronize the recordings
-		// being done by goroutines from previous test cases.
-
-		stream.Mock.On("bla")
-		stream.Mock = mock.Mock{}
-		client.Mock = mock.Mock{}
-		comm.Mock = mock.Mock{}
-	}
-
 	submit := func(rpc *cluster.RPC) error {
 		err := rpc.SendSubmit(1, submitRequest)
 		return err
@@ -139,16 +121,35 @@ func TestSend(t *testing.T) {
 		return rpc.SendConsensus(1, consensusRequest)
 	}
 
-	for _, testCase := range []struct {
+	type testCase struct {
 		name           string
 		method         func(rpc *cluster.RPC) error
-		sendReturns    interface{}
+		sendReturns    error
 		sendCalledWith *orderer.StepRequest
 		receiveReturns []interface{}
 		stepReturns    []interface{}
 		remoteError    error
 		expectedErr    string
-	}{
+	}
+
+	l := &sync.Mutex{}
+	var tst testCase
+
+	sent := make(chan struct{})
+
+	var sendCalls uint32
+
+	stream := &mocks.StepClient{}
+	stream.On("Context", mock.Anything).Return(context.Background())
+	stream.On("Send", mock.Anything).Return(func(*orderer.StepRequest) error {
+		l.Lock()
+		defer l.Unlock()
+		sent <- struct{}{}
+		atomic.AddUint32(&sendCalls, 1)
+		return tst.sendReturns
+	})
+
+	for _, tst := range []testCase{
 		{
 			name:           "Send and Receive submit succeed",
 			method:         submit,
@@ -194,18 +195,15 @@ func TestSend(t *testing.T) {
 			expectedErr: "deadline exceeded",
 		},
 	} {
-		testCase := testCase
+		l.Lock()
+		testCase := tst
+		l.Unlock()
+
 		t.Run(testCase.name, func(t *testing.T) {
+			atomic.StoreUint32(&sendCalls, 0)
 			isSend := testCase.receiveReturns == nil
-			defer resetMocks()
-			var sent sync.WaitGroup
-			sent.Add(1)
-
-			stream.On("Context", mock.Anything).Return(context.Background())
-			stream.On("Send", mock.Anything).Run(func(_ mock.Arguments) {
-				sent.Done()
-			}).Return(testCase.sendReturns)
-			stream.On("Recv").Return(testCase.receiveReturns...)
+			comm := &mocks.Communicator{}
+			client := &mocks.ClusterClient{}
 			client.On("Step", mock.Anything).Return(testCase.stepReturns...)
 			rm := &cluster.RemoteContext{
 				Metrics:      cluster.NewMetrics(&disabled.Provider{}),
@@ -229,8 +227,7 @@ func TestSend(t *testing.T) {
 
 			err = testCase.method(rpc)
 			if testCase.remoteError == nil && testCase.stepReturns[1] == nil {
-				sent.Wait()
-				sent.Add(1)
+				<-sent
 			}
 
 			if testCase.stepReturns[1] == nil && testCase.remoteError == nil {
@@ -245,11 +242,11 @@ func TestSend(t *testing.T) {
 				// to Send() were made
 				err := testCase.method(rpc)
 				if testCase.expectedErr == "" {
-					sent.Wait()
+					<-sent
 				}
 
 				assert.NoError(t, err)
-				stream.AssertNumberOfCalls(t, "Send", 2)
+				assert.Equal(t, int(atomic.LoadUint32(&sendCalls)), 2)
 				client.AssertNumberOfCalls(t, "Step", 1)
 			}
 		})
```
