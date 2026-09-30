# [?] Fix deadlock in the encoder. (#1418)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-03-20
Source: https://github.com/Layr-Labs/eigenda/commit/78f613a2aed7bb63ccd44430c8c42d1e84af7942
Type: security-commit

## Details
Fix deadlock in the encoder. (#1418)

## Patch
### disperser/encoder/server_v2.go
```diff
@@ -39,8 +39,14 @@ type EncoderServerV2 struct {
 	grpcMetrics *grpcprom.ServerMetrics
 	close       func()
 
-	runningRequests chan struct{}
-	requestQueue    chan blobRequest
+	// This channel is used to limit the number of concurrent requests executed by the server. If its capacity
+	// is smaller than the capacity of the backlogLimiter, then the server will process all enqueued requests
+	// in parallel.
+	concurrencyLimiter chan struct{}
+
+	// This channel is used to limit the number of requests that can be enqueued. If this channel is at its limit
+	// and new work is submitted, the server will immediately reject the new request.
+	backlogLimiter chan struct{}
 
 	queueStats map[string]int
 	queueLock  sync.Mutex
@@ -58,16 +64,16 @@ func NewEncoderServerV2(
 	metrics.SetQueueCapacity(config.RequestQueueSize)
 
 	return &EncoderServerV2{
-		config:          config,
-		blobStore:       blobStore,
-		chunkWriter:     chunkWriter,
-		logger:          logger.With("component", "EncoderServerV2"),
-		prover:          prover,
-		metrics:         metrics,
-		grpcMetrics:     grpcMetrics,
-		runningRequests: make(chan struct{}, config.MaxConcurrentRequests),
-		requestQueue:    make(chan blobRequest, config.RequestQueueSize),
-		queueStats:      make(map[string]int),
+		config:             config,
+		blobStore:          blobStore,
+		chunkWriter:        chunkWriter,
+		logger:             logger.With("component", "EncoderServerV2"),
+		prover:             prover,
+		metrics:            metrics,
+		grpcMetrics:        grpcMetrics,
+		concurrencyLimiter: make(chan struct{}, config.MaxConcurrentRequests),
+		backlogLimiter:     make(chan struct{}, config.RequestQueueSize),
+		queueStats:         make(map[string]int),
 	}
 }
 
@@ -110,51 +116,33 @@ func (s *EncoderServerV2) EncodeBlob(ctx context.Context, req *pb.EncodeBlobRequ
 		s.metrics.ObserveLatency("total", time.Since(totalStart))
 	}()
 
-	// Validate request first
+	// Validate the request.
 	blobKey, encodingParams, err := s.validateAndParseRequest(req)
 	if err != nil {
 		return nil, status.Error(codes.InvalidArgument, err.Error())
 	}
-	blobSize := req.GetBlobSize()
-	sizeBucket := common.BlobSizeBucket(int(blobSize))
-
-	// Rate limit
-	select {
-	case s.requestQueue <- blobRequest{blobSizeByte: int(blobSize)}:
-		s.queueLock.Lock()
-		s.queueStats[sizeBucket]++
-		s.metrics.ObserveQueue(s.queueStats)
-		s.queueLock.Unlock()
-	default:
-		s.metrics.IncrementRateLimitedBlobRequestNum(int(blobSize))
-		s.logger.Warn("rate limiting as request queue is full",
-			"requestQueueSize", s.config.RequestQueueSize,
-			"maxConcurrentRequests", s.config.MaxConcurrentRequests)
-		return nil, api.NewErrorResourceExhausted(fmt.Sprintf(
-			"request queue is full, max queue size: %d", s.config.RequestQueueSize))
-	}
+	blobSize := int(req.GetBlobSize())
 
-	// Limit the number of concurrent requests
-
-	select {
-	case s.runningRequests <- struct{}{}:
-		defer s.popRequest()
-	case <-ctx.Done():
-		s.metrics.IncrementCanceledBlobRequestNum(int(blobSize))
-		return nil, status.Error(codes.Canceled, "request was canceled")
+	// If we have too large of a backlog, refuse to accept new work.
+	err = s.pushBacklogLimiter(blobSize)
+	if err != nil {
+		return nil, err
 	}
+	defer s.popBacklogLimiter(blobSize)
 
-	if ctx.Err() != nil {
-		s.metrics.IncrementCanceledBlobRequestNum(int(blobSize))
-		return nil, status.Error(codes.Canceled, "request was canceled")
+	// Limit the number of concurrent requests.
+	err = s.pushConcurrencyLimiter(ctx, blobSize)
+	if err != nil {
+		return nil, err
 	}
+	defer s.popConcurrencyLimiter()
 
 	s.metrics.ObserveLatency("queuing", time.Since(totalStart))
 	reply, err := s.handleEncodingToChunkStore(ctx, blobKey, encodingParams)
 	if err != nil {
-		s.metrics.IncrementFailedBlobRequestNum(int(blobSize))
+		s.metrics.IncrementFailedBlobRequestNum(blobSize)
 	} else {
-		s.metrics.IncrementSuccessfulBlobRequestNum(int(blobSize))
+		s.metrics.IncrementSuccessfulBlobRequestNum(blobSize)
 	}
 
 	return reply, err
@@ -202,15 +190,54 @@ func (s *EncoderServerV2) handleEncodingToChunkStore(ctx context.Context, blobKe
 	return s.processAndStoreResults(ctx, blobKey, frames)
 }
 
-func (s *EncoderServerV2) popRequest() {
-	blobRequest := <-s.requestQueue
-	<-s.runningRequests
+// pushBacklogLimiter pushes a token to the backlog limiter and increments the queue stats accordingly.
+// If there is no capacity in the backlog limiter, an error is returned.
+func (s *EncoderServerV2) pushBacklogLimiter(blobSizeBytes int) error {
+	sizeBucket := common.BlobSizeBucket(blobSizeBytes)
+
+	select {
+	case s.backlogLimiter <- struct{}{}:
+		s.queueLock.Lock()
+		s.queueStats[sizeBucket]++
+		s.metrics.ObserveQueue(s.queueStats)
+		s.queueLock.Unlock()
+
+		return nil
+	default:
+		s.metrics.IncrementRateLimitedBlobRequestNum(blobSizeBytes)
+		s.logger.Warn("rate limiting as request queue is full",
+			"requestQueueSize", s.config.RequestQueueSize,
+			"maxConcurrentRequests", s.config.MaxConcurrentRequests)
+		return api.NewErrorResourceExhausted(fmt.Sprintf(
+			"request queue is full, max queue size: %d", s.config.RequestQueueSize))
+	}
+}
+
+// popBacklogLimiter pops a token from the backlog limiter and decrements the queue stats accordingly.
+func (s *EncoderServerV2) popBacklogLimiter(blobSizeBytes int) {
+	<-s.backlogLimiter
 	s.queueLock.Lock()
-	s.queueStats[common.BlobSizeBucket(blobRequest.blobSizeByte)]--
+	s.queueStats[common.BlobSizeBucket(blobSizeBytes)]--
 	s.metrics.ObserveQueue(s.queueStats)
 	s.queueLock.Unlock()
 }
 
+// pushConcurrencyLimiter pushes a token to the concurrency limiter.
+func (s *EncoderServerV2) pushConcurrencyLimiter(ctx context.Context, blobSizeBytes int) error {
+	select {
+	case s.concurrencyLimiter <- struct{}{}:
+		return nil
+	case <-ctx.Done():
+		s.metrics.IncrementCanceledBlobRequestNum(blobSizeBytes)
+		return status.Error(codes.Canceled, "request was canceled")
+	}
+}
+
+// popConcurrencyLimiter pops a token from the concurrency limiter.
+func (s *EncoderServerV2) popConcurrencyLimiter() {
+	<-s.concurrencyLimiter
+}
+
 func (s *EncoderServerV2) validateAndParseRequest(req *pb.EncodeBlobRequest) (corev2.BlobKey, encoding.EncodingParams, error) {
 	// Create zero values for return types
 	var (
```
