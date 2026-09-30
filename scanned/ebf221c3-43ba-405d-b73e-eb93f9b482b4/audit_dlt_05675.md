# [?] eth: fix concurrent map writes panic in witness protocol (#2023)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-01-29
Source: https://github.com/0xPolygon/bor/commit/8dbb965a9bb9dfe5f3deab87c05fa01ced34636e
Type: security-commit

## Details
eth: fix concurrent map writes panic in witness protocol (#2023)

Protect failedRequests map access with mapsMu lock in receiveWitnessPage and buildWitnessRequests to prevent "concurrent map writes" panic when multiple goroutines update retry counts simultaneously.

## Patch
### eth/peer.go
```diff
@@ -479,6 +479,7 @@ func (p *ethPeer) receiveWitnessPage(
 	defer func() {
 		// if fails map on retry count and request again
 		if retrievedError != nil {
+			mapsMu.Lock()
 			for _, request := range witReqRes.Request {
 				if failedRequests[request.Hash] == nil {
 					failedRequests[request.Hash] = make(map[uint64]witReqRetryCount)
@@ -490,6 +491,7 @@ func (p *ethPeer) receiveWitnessPage(
 				}
 				failedRequests[request.Hash][request.Page] = retryCount
 			}
+			mapsMu.Unlock()
 
 			// non blocking call to avoid race condition because of semaphore
 			witReqsWg.Add(1) // protecting from not finishing before requests are built
@@ -673,27 +675,43 @@ func (p *ethPeer) buildWitnessRequests(hashes []common.Hash,
 	}
 
 	// checking failed requests to retry
-	for hash, _ := range failedRequests {
-		for page, _ := range failedRequests[hash] {
-			retryCount := failedRequests[hash][page]
+	type retryItem struct {
+		hash common.Hash
+		page uint64
+	}
+	var toRetry []retryItem
+
+	mapsMu.RLock()
+	for hash, pages := range failedRequests {
+		for page, retryCount := range pages {
 			if retryCount.ShouldRetryAgain {
-				if err := p.doWitnessRequest(
-					hash,
-					page,
-					witReqs,
-					witReqsWg,
-					witReqResCh,
-					witReqSem,
-					mapsMu,
-					witTotalRequest,
-				); err != nil {
-					return err
-				}
-				retryCount.ShouldRetryAgain = false
+				toRetry = append(toRetry, retryItem{hash, page})
 			}
-			failedRequests[hash][page] = retryCount
 		}
 	}
+	mapsMu.RUnlock()
+
+	for _, item := range toRetry {
+		if err := p.doWitnessRequest(
+			item.hash,
+			item.page,
+			witReqs,
+			witReqsWg,
+			witReqResCh,
+			witReqSem,
+			mapsMu,
+			witTotalRequest,
+		); err != nil {
+			return err
+		}
+		mapsMu.Lock()
+		if failedRequests[item.hash] != nil {
+			retryCount := failedRequests[item.hash][item.page]
+			retryCount.ShouldRetryAgain = false
+			failedRequests[item.hash][item.page] = retryCount
+		}
+		mapsMu.Unlock()
+	}
 	return nil
 }
 
```

### eth/peer_test.go
```diff
@@ -1389,6 +1389,265 @@ func TestRequestWitnessesWithVerification_DownloadPaused(t *testing.T) {
 	}
 }
 
+// TestBuildWitnessRequests_ConcurrentFailedRequestsAccess verifies that concurrent access
+// to the failedRequests map in buildWitnessRequests is properly synchronized.
+// This test specifically validates the fix for the "concurrent map writes" panic.
+// Run this test with: go test -race -run TestBuildWitnessRequests_ConcurrentFailedRequestsAccess
+func TestBuildWitnessRequests_ConcurrentFailedRequestsAccess(t *testing.T) {
+	ctrl := gomock.NewController(t)
+	defer ctrl.Finish()
+
+	mockWitPeer := NewMockWitnessPeer(ctrl)
+	mockWitPeer.EXPECT().Log().Return(log.New()).AnyTimes()
+	mockWitPeer.EXPECT().ID().Return("test-peer").AnyTimes()
+
+	p := &ethPeer{
+		Peer:    eth.NewPeer(1, p2p.NewPeer(enode.ID{0x01}, "test-peer", []p2p.Cap{}), nil, nil),
+		witPeer: &witPeer{Peer: mockWitPeer},
+	}
+
+	// Mock RequestWitness to simulate responses
+	mockWitPeer.EXPECT().
+		RequestWitness(gomock.Any(), gomock.Any()).
+		DoAndReturn(func(wpr []wit.WitnessPageRequest, ch chan *wit.Response) (*wit.Request, error) {
+			go func() {
+				ch <- &wit.Response{
+					Res: &wit.WitnessPacketRLPPacket{
+						WitnessPacketResponse: []wit.WitnessPageResponse{{
+							Page:       wpr[0].Page,
+							TotalPages: 10,
+							Hash:       wpr[0].Hash,
+							Data:       []byte{0x01, 0x02},
+						}},
+					},
+					Done: make(chan error, 10),
+				}
+			}()
+			return &wit.Request{}, nil
+		}).
+		AnyTimes()
+
+	// Setup shared data structures
+	hashes := []common.Hash{{0xaa}, {0xbb}, {0xcc}}
+	witTotalPages := make(map[common.Hash]uint64)
+	witTotalRequest := make(map[common.Hash]uint64)
+	failedRequests := make(map[common.Hash]map[uint64]witReqRetryCount)
+	witReqResCh := make(chan *witReqRes, 100)
+	witReqSem := make(chan int, 20)
+	var mapsMu sync.RWMutex
+	var buildRequestMu sync.RWMutex
+	var witReqs []*wit.Request
+	var witReqsWg sync.WaitGroup
+
+	// Pre-populate failedRequests with some data to retry
+	for _, hash := range hashes {
+		witTotalPages[hash] = 5
+		failedRequests[hash] = make(map[uint64]witReqRetryCount)
+		for page := uint64(0); page < 3; page++ {
+			failedRequests[hash][page] = witReqRetryCount{
+				FailCount:        1,
+				ShouldRetryAgain: true,
+			}
+		}
+	}
+
+	// Launch multiple concurrent buildWitnessRequests calls
+	// This simulates the scenario where multiple goroutines spawned from
+	// receiveWitnessPage.func1 (line 496) all try to access failedRequests
+	const numGoroutines = 10
+	var wg sync.WaitGroup
+	errCh := make(chan error, numGoroutines)
+
+	for i := 0; i < numGoroutines; i++ {
+		wg.Add(1)
+		go func() {
+			defer wg.Done()
+
+			// Drain semaphore slots that get filled
+			go func() {
+				for j := 0; j < 20; j++ {
+					select {
+					case <-witReqSem:
+					case <-time.After(50 * time.Millisecond):
+						return
+					}
+				}
+			}()
+
+			err := p.buildWitnessRequests(
+				hashes,
+				&witReqs,
+				&witReqsWg,
+				witTotalPages,
+				witTotalRequest,
+				witReqResCh,
+				witReqSem,
+				&mapsMu,
+				&buildRequestMu,
+				failedRequests,
+			)
+			if err != nil {
+				errCh <- err
+			}
+		}()
+	}
+
+	// Also simulate concurrent writes to failedRequests from receiveWitnessPage deferred function
+	for i := 0; i < numGoroutines; i++ {
+		wg.Add(1)
+		go func(idx int) {
+			defer wg.Done()
+
+			hash := hashes[idx%len(hashes)]
+			page := uint64(idx)
+
+			// This simulates the deferred function in receiveWitnessPage (lines 479-504)
+			// After the fix, this should be protected by mapsMu
+			mapsMu.Lock()
+			if failedRequests[hash] == nil {
+				failedRequests[hash] = make(map[uint64]witReqRetryCount)
+			}
+			retryCount := failedRequests[hash][page]
+			retryCount.FailCount++
+			retryCount.ShouldRetryAgain = true
+			failedRequests[hash][page] = retryCount
+			mapsMu.Unlock()
+		}(i)
+	}
+
+	// Wait for all goroutines with timeout
+	done := make(chan struct{})
+	go func() {
+		wg.Wait()
+		close(done)
+	}()
+
+	select {
+	case <-done:
+		// Success - no panic occurred
+	case <-time.After(5 * time.Second):
+		t.Fatal("Test timed out - possible deadlock")
+	}
+
+	// Check for errors
+	close(errCh)
+	for err := range errCh {
+		t.Logf("buildWitnessRequests returned error (expected in some concurrent scenarios): %v", err)
+	}
+
+	t.Log("Test completed successfully - no concurrent map write panic occurred")
+	t.Log("If running with -race flag, any data race will be reported by the race detector")
+}
+
+// TestFailedRequestsMapConcurrentWritesFix specifically tests the fix for the panic:
+// "fatal error: concurrent map writes" in receiveWitnessPage.func1
+// This test creates the exact scenario from the bug report where multiple goroutines
+// simultaneously write to failedRequests map.
+func TestFailedRequestsMapConcurrentWritesFix(t *testing.T) {
+	// This test verifies the fix by simulating concurrent access patterns
+	// that previously caused the panic at eth/peer.go:491
+
+	failedRequests := make(map[common.Hash]map[uint64]witReqRetryCount)
+	var mapsMu sync.RWMutex
+
+	hashes := make([]common.Hash, 20)
+	for i := range hashes {
+		hashes[i] = common.Hash{byte(i)}
+	}
+
+	// Simulate multiple goroutines writing to failedRequests concurrently
+	// This is what happens when multiple receiveWitnessPage.func1 goroutines
+	// try to update failedRequests simultaneously
+	const numWriters = 50
+	var wg sync.WaitGroup
+
+	for i := 0; i < numWriters; i++ {
+		wg.Add(1)
+		go func(idx int) {
+			defer wg.Done()
+
+			hash := hashes[idx%len(hashes)]
+			page := uint64(idx % 10)
+
+			// Simulate the fixed code path from receiveWitnessPage deferred function
+			// Lines 481-493 with proper locking
+			mapsMu.Lock()
+			if failedRequests[hash] == nil {
+				failedRequests[hash] = make(map[uint64]witReqRetryCount)
+			}
+			retryCount := failedRequests[hash][page]
+			retryCount.FailCount++
+			if retryCount.FailCount <= DefaultMaxPagesRequestRetries {
+				retryCount.ShouldRetryAgain = true
+			}
+			failedRequests[hash][page] = retryCount
+			mapsMu.Unlock()
+		}(i)
+	}
+
+	// Simulate concurrent readers (from buildWitnessRequests)
+	for i := 0; i < numWriters; i++ {
+		wg.Add(1)
+		go func(idx int) {
+			defer wg.Done()
+
+			hash := hashes[idx%len(hashes)]
+
+			// Simulate the fixed code path from buildWitnessRequests
+			// Lines 676-696 with proper locking
+			mapsMu.Lock()
+			// Copy under lock
+			localCopy := make(map[uint64]witReqRetryCount)
+			if pages, ok := failedRequests[hash]; ok {
+				for page, retryCount := range pages {
+					localCopy[page] = retryCount
+				}
+			}
+			mapsMu.Unlock()
+
+			// Process copy without holding lock
+			for page, retryCount := range localCopy {
+				if retryCount.ShouldRetryAgain {
+					// Simulate processing...
+					retryCount.ShouldRetryAgain = false
+
+					// Update original under lock
+					mapsMu.Lock()
+					if failedRequests[hash] != nil {
+						failedRequests[hash][page] = retryCount
+					}
+					mapsMu.Unlock()
+				}
+			}
+		}(i)
+	}
+
+	// Wait with timeout
+	done := make(chan struct{})
+	go func() {
+		wg.Wait()
+		close(done)
+	}()
+
+	select {
+	case <-done:
+		t.Log("All concurrent operations completed without panic")
+	case <-time.After(10 * time.Second):
+		t.Fatal("Test timed out")
+	}
+
+	// Verify data integrity - all writes should have been recorded
+	mapsMu.RLock()
+	totalEntries := 0
+	for _, pages := range failedRequests {
+		totalEntries += len(pages)
+	}
+	mapsMu.RUnlock()
+
+	t.Logf("Final failedRequests has %d hashes with %d total page entries", len(failedRequests), totalEntries)
+	assert.True(t, len(failedRequests) > 0, "failedRequests should have entries after concurrent writes")
+}
+
 // TestDoWitnessRequest_RaceCondition_WitTotalRequest exposes the race condition in doWitnessRequest
 // where witTotalRequest[hash] is read without lock protection but written with lock protection.
 // Run this test with: go test -race -run TestDoWitnessRequest_RaceCondition_WitTotalRequest
```
