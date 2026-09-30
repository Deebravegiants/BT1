# [?] fix: use Counter for nonceFailureCache overflow metric (#3648)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-09-29
Source: https://github.com/OffchainLabs/nitro/commit/cf87312f3dccdf0ec22de427c3b9173f80a4d03f
Type: security-commit

## Details
fix: use Counter for nonceFailureCache overflow metric (#3648)

* Update sequencer.go

* Update restful_server.go

* Update dasRpcServer.go

* Update dasRpcClient.go

* Update validation_client.go

* Update dasRpcClient.go

* Update dasRpcServer.go

* Update restful_server.go

* Update validation_client.go

* lint

* ci fix

---------

Co-authored-by: Pepper Lebeck-Jobe <pepper@offchainlabs.com>
Co-authored-by: Tristan-Wilson <87238672+Tristan-Wilson@users.noreply.github.com>

## Patch
### daprovider/das/dasRpcClient.go
```diff
@@ -23,11 +23,11 @@ import (
 )
 
 var (
-	rpcClientStoreRequestGauge      = metrics.NewRegisteredGauge("arb/das/rpcclient/store/requests", nil)
-	rpcClientStoreSuccessGauge      = metrics.NewRegisteredGauge("arb/das/rpcclient/store/success", nil)
-	rpcClientStoreFailureGauge      = metrics.NewRegisteredGauge("arb/das/rpcclient/store/failure", nil)
-	rpcClientStoreStoredBytesGauge  = metrics.NewRegisteredGauge("arb/das/rpcclient/store/bytes", nil)
-	rpcClientStoreDurationHistogram = metrics.NewRegisteredHistogram("arb/das/rpcclient/store/duration", nil, metrics.NewBoundedHistogramSample())
+	rpcClientStoreRequestCounter     = metrics.NewRegisteredCounter("arb/das/rpcclient/store/requests", nil)
+	rpcClientStoreSuccessCounter     = metrics.NewRegisteredCounter("arb/das/rpcclient/store/success", nil)
+	rpcClientStoreFailureCounter     = metrics.NewRegisteredCounter("arb/das/rpcclient/store/failure", nil)
+	rpcClientStoreStoredBytesCounter = metrics.NewRegisteredCounter("arb/das/rpcclient/store/bytes", nil)
+	rpcClientStoreDurationHistogram  = metrics.NewRegisteredHistogram("arb/das/rpcclient/store/duration", nil, metrics.NewBoundedHistogramSample())
 )
 
 // lint:require-exhaustive-initialization
@@ -77,14 +77,14 @@ func NewDASRPCClient(target string, signer signature.DataSignerFunc, maxStoreChu
 }
 
 func (c *DASRPCClient) Store(ctx context.Context, message []byte, timeout uint64) (*dasutil.DataAvailabilityCertificate, error) {
-	rpcClientStoreRequestGauge.Inc(1)
+	rpcClientStoreRequestCounter.Inc(1)
 	start := time.Now()
 	success := false
 	defer func() {
 		if success {
-			rpcClientStoreSuccessGauge.Inc(1)
+			rpcClientStoreSuccessCounter.Inc(1)
 		} else {
-			rpcClientStoreFailureGauge.Inc(1)
+			rpcClientStoreFailureCounter.Inc(1)
 		}
 		rpcClientStoreDurationHistogram.Update(time.Since(start).Nanoseconds())
 	}()
@@ -108,7 +108,7 @@ func (c *DASRPCClient) Store(ctx context.Context, message []byte, timeout uint64
 		return nil, err
 	}
 
-	rpcClientStoreStoredBytesGauge.Inc(int64(len(message)))
+	rpcClientStoreStoredBytesCounter.Inc(int64(len(message)))
 	success = true
 
 	return &dasutil.DataAvailabilityCertificate{
```

### daprovider/das/dasRpcServer.go
```diff
@@ -24,14 +24,14 @@ import (
 )
 
 var (
-	rpcStoreRequestGauge      = metrics.NewRegisteredGauge("arb/das/rpc/store/requests", nil)
-	rpcStoreSuccessGauge      = metrics.NewRegisteredGauge("arb/das/rpc/store/success", nil)
-	rpcStoreFailureGauge      = metrics.NewRegisteredGauge("arb/das/rpc/store/failure", nil)
-	rpcStoreStoredBytesGauge  = metrics.NewRegisteredGauge("arb/das/rpc/store/bytes", nil)
-	rpcStoreDurationHistogram = metrics.NewRegisteredHistogram("arb/das/rpc/store/duration", nil, metrics.NewBoundedHistogramSample())
-
-	rpcSendChunkSuccessGauge = metrics.NewRegisteredGauge("arb/das/rpc/sendchunk/success", nil)
-	rpcSendChunkFailureGauge = metrics.NewRegisteredGauge("arb/das/rpc/sendchunk/failure", nil)
+	rpcStoreRequestCounter     = metrics.NewRegisteredCounter("arb/das/rpc/store/requests", nil)
+	rpcStoreSuccessCounter     = metrics.NewRegisteredCounter("arb/das/rpc/store/success", nil)
+	rpcStoreFailureCounter     = metrics.NewRegisteredCounter("arb/das/rpc/store/failure", nil)
+	rpcStoreStoredBytesCounter = metrics.NewRegisteredCounter("arb/das/rpc/store/bytes", nil)
+	rpcStoreDurationHistogram  = metrics.NewRegisteredHistogram("arb/das/rpc/store/duration", nil, metrics.NewBoundedHistogramSample())
+
+	rpcSendChunkSuccessCounter = metrics.NewRegisteredCounter("arb/das/rpc/sendchunk/success", nil)
+	rpcSendChunkFailureCounter = metrics.NewRegisteredCounter("arb/das/rpc/sendchunk/failure", nil)
 )
 
 const (
@@ -79,7 +79,7 @@ func StartDASRPCServerOnListener(ctx context.Context, listener net.Listener, rpc
 		daHealthChecker:   daHealthChecker,
 		signatureVerifier: signatureVerifier,
 		dataStreamReceiver: data_streaming.NewDataStreamReceiver(dataStreamPayloadVerifier, defaultMaxPendingMessages, defaultMessageCollectionExpiry, func(id data_streaming.MessageId) {
-			rpcStoreFailureGauge.Inc(1)
+			rpcStoreFailureCounter.Inc(1)
 		}),
 	})
 	if err != nil {
@@ -121,14 +121,14 @@ type StoreResult struct {
 func (s *DASRPCServer) Store(ctx context.Context, message hexutil.Bytes, timeout hexutil.Uint64, sig hexutil.Bytes) (*StoreResult, error) {
 	// #nosec G115
 	log.Trace("dasRpc.DASRPCServer.Store", "message", pretty.FirstFewBytes(message), "message length", len(message), "timeout", time.Unix(int64(timeout), 0), "sig", pretty.FirstFewBytes(sig), "this", s)
-	rpcStoreRequestGauge.Inc(1)
+	rpcStoreRequestCounter.Inc(1)
 	start := time.Now()
 	success := false
 	defer func() {
 		if success {
-			rpcStoreSuccessGauge.Inc(1)
+			rpcStoreSuccessCounter.Inc(1)
 		} else {
-			rpcStoreFailureGauge.Inc(1)
+			rpcStoreFailureCounter.Inc(1)
 		}
 		rpcStoreDurationHistogram.Update(time.Since(start).Nanoseconds())
 	}()
@@ -141,7 +141,7 @@ func (s *DASRPCServer) Store(ctx context.Context, message hexutil.Bytes, timeout
 	if err != nil {
 		return nil, err
 	}
-	rpcStoreStoredBytesGauge.Inc(int64(len(message)))
+	rpcStoreStoredBytesCounter.Inc(int64(len(message)))
 	success = true
 	return &StoreResult{
 		KeysetHash:  cert.KeysetHash[:],
@@ -159,11 +159,11 @@ var (
 )
 
 func (s *DASRPCServer) StartChunkedStore(ctx context.Context, timestamp, nChunks, chunkSize, totalSize, timeout hexutil.Uint64, sig hexutil.Bytes) (*data_streaming.StartStreamingResult, error) {
-	rpcStoreRequestGauge.Inc(1)
+	rpcStoreRequestCounter.Inc(1)
 	failed := true
 	defer func() {
 		if failed {
-			rpcStoreFailureGauge.Inc(1)
+			rpcStoreFailureCounter.Inc(1)
 		}
 	}()
 
@@ -180,9 +180,9 @@ func (s *DASRPCServer) SendChunk(ctx context.Context, messageId, chunkId hexutil
 	success := false
 	defer func() {
 		if success {
-			rpcSendChunkSuccessGauge.Inc(1)
+			rpcSendChunkSuccessCounter.Inc(1)
 		} else {
-			rpcSendChunkFailureGauge.Inc(1)
+			rpcSendChunkFailureCounter.Inc(1)
 		}
 	}()
 
@@ -204,16 +204,16 @@ func (s *DASRPCServer) CommitChunkedStore(ctx context.Context, messageId hexutil
 	success := false
 	defer func() {
 		if success {
-			rpcStoreSuccessGauge.Inc(1)
+			rpcStoreSuccessCounter.Inc(1)
 		} else {
-			rpcStoreFailureGauge.Inc(1)
+			rpcStoreFailureCounter.Inc(1)
 		}
 		rpcStoreDurationHistogram.Update(time.Since(startTime).Nanoseconds())
 	}()
 	if err != nil {
 		return nil, err
 	}
-	rpcStoreStoredBytesGauge.Inc(int64(len(message)))
+	rpcStoreStoredBytesCounter.Inc(int64(len(message)))
 	success = true
 	return &StoreResult{
 		KeysetHash:  cert.KeysetHash[:],
```

### daprovider/das/restful_server.go
```diff
@@ -24,11 +24,11 @@ import (
 )
 
 var (
-	restGetByHashRequestGauge       = metrics.NewRegisteredGauge("arb/das/rest/getbyhash/requests", nil)
-	restGetByHashSuccessGauge       = metrics.NewRegisteredGauge("arb/das/rest/getbyhash/success", nil)
-	restGetByHashFailureGauge       = metrics.NewRegisteredGauge("arb/das/rest/getbyhash/failure", nil)
-	restGetByHashReturnedBytesGauge = metrics.NewRegisteredGauge("arb/das/rest/getbyhash/bytes", nil)
-	restGetByHashDurationHistogram  = metrics.NewRegisteredHistogram("arb/das/rest/getbyhash/duration", nil, metrics.NewBoundedHistogramSample())
+	restGetByHashRequestCounter       = metrics.NewRegisteredCounter("arb/das/rest/getbyhash/requests", nil)
+	restGetByHashSuccessCounter       = metrics.NewRegisteredCounter("arb/das/rest/getbyhash/success", nil)
+	restGetByHashFailureCounter       = metrics.NewRegisteredCounter("arb/das/rest/getbyhash/failure", nil)
+	restGetByHashReturnedBytesCounter = metrics.NewRegisteredCounter("arb/das/rest/getbyhash/bytes", nil)
+	restGetByHashDurationHistogram    = metrics.NewRegisteredHistogram("arb/das/rest/getbyhash/duration", nil, metrics.NewBoundedHistogramSample())
 )
 
 type RestfulDasServer struct {
@@ -140,14 +140,14 @@ func (rds *RestfulDasServer) ExpirationPolicyHandler(w http.ResponseWriter, r *h
 
 func (rds *RestfulDasServer) GetByHashHandler(w http.ResponseWriter, r *http.Request, requestPath string) {
 	log.Debug("Got request", "requestPath", requestPath)
-	restGetByHashRequestGauge.Inc(1)
+	restGetByHashRequestCounter.Inc(1)
 	start := time.Now()
 	success := false
 	defer func() {
 		if success {
-			restGetByHashSuccessGauge.Inc(1)
+			restGetByHashSuccessCounter.Inc(1)
 		} else {
-			restGetByHashFailureGauge.Inc(1)
+			restGetByHashFailureCounter.Inc(1)
 		}
 		restGetByHashDurationHistogram.Update(time.Since(start).Nanoseconds())
 	}()
@@ -176,7 +176,7 @@ func (rds *RestfulDasServer) GetByHashHandler(w http.ResponseWriter, r *http.Req
 	base64.StdEncoding.Encode(encodedResponseData, responseData)
 	var response RestfulDasServerResponse
 	response.Data = string(encodedResponseData)
-	restGetByHashReturnedBytesGauge.Inc(int64(len(response.Data)))
+	restGetByHashReturnedBytesCounter.Inc(int64(len(response.Data)))
 
 	err = json.NewEncoder(w).Encode(response)
 	if err != nil {
```

### execution/gethexec/sequencer.go
```diff
@@ -50,7 +50,7 @@ var (
 	nonceCacheRejectedCounter               = metrics.NewRegisteredCounter("arb/sequencer/noncecache/rejected", nil)
 	nonceCacheClearedCounter                = metrics.NewRegisteredCounter("arb/sequencer/noncecache/cleared", nil)
 	nonceFailureCacheSizeGauge              = metrics.NewRegisteredGauge("arb/sequencer/noncefailurecache/size", nil)
-	nonceFailureCacheOverflowCounter        = metrics.NewRegisteredGauge("arb/sequencer/noncefailurecache/overflow", nil)
+	nonceFailureCacheOverflowCounter        = metrics.NewRegisteredCounter("arb/sequencer/noncefailurecache/overflow", nil)
 	blockCreationTimer                      = metrics.NewRegisteredHistogram("arb/sequencer/block/creation", nil, metrics.NewBoundedHistogramSample())
 	successfulBlocksCounter                 = metrics.NewRegisteredCounter("arb/sequencer/block/successful", nil)
 	conditionalTxRejectedBySequencerCounter = metrics.NewRegisteredCounter("arb/sequencer/conditionaltx/rejected", nil)
```

### validator/client/validation_client.go
```diff
@@ -26,7 +26,7 @@ import (
 	"github.com/offchainlabs/nitro/validator/server_common"
 )
 
-var executionNodeOfflineGauge = metrics.NewRegisteredGauge("arb/state_provider/execution_node_offline", nil)
+var executionNodeOfflineCounter = metrics.NewRegisteredCounter("arb/state_provider/execution_node_offline", nil)
 
 type ValidationClient struct {
 	stopwaiter.StopWaiter
@@ -238,7 +238,7 @@ func ctxWithCheckAlive(ctxIn context.Context, execRun validator.ExecutionRun) (c
 				ctxCheckAliveWithTimeout, cancelCheckAliveWithTimeout := context.WithTimeout(ctx, 5*time.Second)
 				err := execRun.CheckAlive(ctxCheckAliveWithTimeout)
 				if err != nil {
-					executionNodeOfflineGauge.Inc(1)
+					executionNodeOfflineCounter.Inc(1)
 					cancelCheckAliveWithTimeout()
 					return
 				}
```
