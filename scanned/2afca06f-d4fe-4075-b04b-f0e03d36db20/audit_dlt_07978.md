# [?] eth/peer(wit): fix nil pointer dereferences in RequestWitnesses (#1738)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2025-08-29
Source: https://github.com/0xPolygon/bor/commit/d21479728d89e55b38e24244b9188fab519e08b1
Type: security-commit

## Details
eth/peer(wit): fix nil pointer dereferences in RequestWitnesses (#1738)

* fix: nil pointer dereference cases in RequestWitnesses and unit tests

* chore: nit

## Patch
### eth/peer.go
```diff
@@ -212,11 +212,46 @@ func (p *ethPeer) RequestWitnesses(hashes []common.Hash, dlResCh chan *eth.Respo
 			p.receiveWitnessPage(witRes, receivedWitPages, reconstructedWitness, hashes, &witReqs, &witReqsWg, witTotalPages, witTotalRequest, witReqResCh, witReqSem, &mapsMu, &buildRequestMu, failedRequests)
 
 			<-witReqSem
-			witRes.Response.Done <- nil
+			// Check if the Response is nil before accessing the Done channel.
+			if witRes.Response != nil && witRes.Response.Done != nil {
+				witRes.Response.Done <- nil
+				lastWitRes = witRes.Response
+			}
 			witReqsWg.Done()
-			lastWitRes = witRes.Response
 		}
-		p.witPeer.Peer.Log().Trace("RequestWitnesses adapter received all responses", "peer", p.ID())
+		p.witPeer.Peer.Log().Trace("RequestWitnesses adapter finished receiving responses", "peer", p.ID())
+
+		// Check if we successfully received and processed witness data from the peer.
+		// This prevents nil pointer dereference by checking multiple failure scenarios.
+		// - len(receivedWitPages) == 0: No witness pages received at all.
+		// - len(reconstructedWitness) == 0: No witness data reconstructed from the received pages.
+		// - lastWitRes == nil: Same as len(reconstructedWitness) == 0, because if we have even one valid witness, lastWitRes will not be nil.
+		if len(receivedWitPages) == 0 || len(reconstructedWitness) == 0 || lastWitRes == nil {
+			p.witPeer.Peer.Log().Warn("Empty response received for witnesses requested from peer", "peer", p.ID(), "requestedHashes", hashes)
+
+			doneCh := make(chan error)
+			go func() {
+				<-doneCh
+			}()
+
+			emptyWitnesses := make([]*stateless.Witness, 0)
+			emptyRes := &eth.Response{
+				Req:  wrapperReq.Request,
+				Res:  emptyWitnesses,
+				Meta: nil,
+				Time: 0,
+				Done: doneCh,
+			}
+
+			select {
+			case dlResCh <- emptyRes:
+				p.witPeer.Peer.Log().Trace("RequestWitnesses sent empty response because of empty witness data received from peer", "peer", p.ID())
+			case <-wrapperReq.Request.Cancel:
+				p.witPeer.Peer.Log().Trace("RequestWitnesses cancelled before sending empty response", "peer", p.ID())
+				return
+			}
+			return
+		}
 
 		var witnesses []*stateless.Witness
 		var responseHashes []common.Hash
@@ -241,7 +276,7 @@ func (p *ethPeer) RequestWitnesses(hashes []common.Hash, dlResCh chan *eth.Respo
 			Res:  witnesses,
 			Meta: lastWitRes.Meta,
 			Time: lastWitRes.Time,
-			Done: doneCh, // sends a ephemeral doneCh to keep compatibility
+			Done: doneCh, // Send an ephemeral doneCh to keep compatibility.
 		}
 
 		// Forward the adapted response to the downloader's channel,
@@ -302,6 +337,13 @@ func (p *ethPeer) receiveWitnessPage(
 			}()
 		}
 	}()
+
+	// Check if the Response is nil.
+	if witReqRes.Response == nil {
+		p.witPeer.Peer.Log().Warn("RequestWitnesses received nil response from peer", "peer", p.ID())
+		return errors.New("received nil response")
+	}
+
 	witPacketPtr, ok := witReqRes.Response.Res.(*wit.WitnessPacketRLPPacket)
 	if !ok {
 		p.witPeer.Peer.Log().Error("RequestWitnesses received unexpected response type", "type", fmt.Sprintf("%T", witReqRes.Response), "peer", p.ID())
```

### eth/peer_test.go
```diff
@@ -190,3 +190,170 @@ func FillWitnessWithDeterministicRandomState(w *stateless.Witness, targetSize in
 		total += chunkSize
 	}
 }
+
+// TestRequestWitnesses_PeerDisconnectionNoPanic tests that when a peer disconnects
+// before any responses are received, the function gracefully handles the situation
+// without panicking due to nil pointer dereference.
+func TestRequestWitnesses_PeerDisconnectionNoPanic(t *testing.T) {
+	ctrl := gomock.NewController(t)
+	defer ctrl.Finish()
+
+	hashToRequest := common.Hash{123}
+	mockWitPeer := NewMockWitnessPeer(ctrl)
+	p := &ethPeer{
+		Peer:    eth.NewPeer(1, p2p.NewPeer(enode.ID{0x01, 0x02}, "test-peer", []p2p.Cap{}), nil, nil),
+		witPeer: &witPeer{Peer: mockWitPeer},
+	}
+	dlCh := make(chan *eth.Response, 1)
+
+	mockWitPeer.EXPECT().Log().Return(log.New()).AnyTimes()
+
+	// Mock RequestWitness to simulate immediate failure (peer disconnection).
+	mockWitPeer.
+		EXPECT().
+		RequestWitness(gomock.Any(), gomock.Any()).
+		DoAndReturn(func(wpr []wit.WitnessPageRequest, ch chan *wit.Response) (*wit.Request, error) {
+			// Close the channel immediately to simulate no responses.
+			go func() {
+				// Immediately close the channel without sending anything.
+				close(ch)
+			}()
+			return &wit.Request{}, nil
+		}).
+		AnyTimes()
+
+	// Call RequestWitnesses.
+	req, err := p.RequestWitnesses([]common.Hash{hashToRequest}, dlCh)
+
+	// Verify no error during setup.
+	assert.NoError(t, err)
+	assert.NotNil(t, req, "expected a non-nil *eth.Request")
+
+	// Wait for response - should receive empty response instead of panic.
+	select {
+	case response := <-dlCh:
+		assert.NotNil(t, response, "should receive a response")
+		assert.NotNil(t, response.Res, "response should have non-nil Res field")
+
+		// Verify it's an empty witness slice, not nil.
+		witnesses, ok := response.Res.([]*stateless.Witness)
+		assert.True(t, ok, "response should contain []*stateless.Witness")
+		assert.Equal(t, 0, len(witnesses), "should receive empty witness slice")
+
+		// Verify other fields are handled correctly.
+		assert.NotNil(t, response.Req, "should have request reference")
+		assert.NotNil(t, response.Done, "should have Done channel")
+		assert.Nil(t, response.Meta, "should have nil Meta when no responses received")
+		assert.Equal(t, time.Duration(0), response.Time, "should have zero time when no responses received")
+
+	case <-time.After(2 * time.Second):
+		t.Fatal("timed out waiting for response")
+	}
+}
+
+// TestRequestWitnesses_EmptyResponsesNoPanic tests the case where responses are received
+// but they contain no usable witness data, ensuring no panic occurs.
+func TestRequestWitnesses_EmptyResponsesNoPanic(t *testing.T) {
+	ctrl := gomock.NewController(t)
+	defer ctrl.Finish()
+
+	hashToRequest := common.Hash{123}
+	mockWitPeer := NewMockWitnessPeer(ctrl)
+	p := &ethPeer{
+		Peer:    eth.NewPeer(1, p2p.NewPeer(enode.ID{0x01, 0x02}, "test-peer", []p2p.Cap{}), nil, nil),
+		witPeer: &witPeer{Peer: mockWitPeer},
+	}
+	dlCh := make(chan *eth.Response, 1)
+
+	mockWitPeer.EXPECT().Log().Return(log.New()).AnyTimes()
+
+	// Mock RequestWitness to send empty/invalid responses.
+	mockWitPeer.
+		EXPECT().
+		RequestWitness(gomock.Any(), gomock.Any()).
+		DoAndReturn(func(wpr []wit.WitnessPageRequest, ch chan *wit.Response) (*wit.Request, error) {
+			go func() {
+				// Send response with empty data (simulates corrupted or empty witness pages).
+				ch <- &wit.Response{
+					Res: &wit.WitnessPacketRLPPacket{
+						WitnessPacketResponse: []wit.WitnessPageResponse{{
+							Page:       0,
+							TotalPages: 1,
+							Hash:       hashToRequest,
+							Data:       []byte{}, // Empty data
+						}},
+					},
+					Done: make(chan error, 1),
+				}
+			}()
+			return &wit.Request{}, nil
+		}).
+		Times(1)
+
+	// Call RequestWitnesses.
+	req, err := p.RequestWitnesses([]common.Hash{hashToRequest}, dlCh)
+	assert.NoError(t, err)
+	assert.NotNil(t, req)
+
+	// Wait for response.
+	select {
+	case response := <-dlCh:
+		assert.NotNil(t, response)
+		witnesses, ok := response.Res.([]*stateless.Witness)
+		assert.True(t, ok, "should receive []*stateless.Witness type")
+		assert.Equal(t, 0, len(witnesses), "should receive empty witness slice when no valid witnesses reconstructed")
+
+	case <-time.After(2 * time.Second):
+		t.Fatal("timed out waiting for response")
+	}
+}
+
+// TestRequestWitnesses_PartialFailureNoPanic tests that when some witness pages fail
+// to be received or reconstructed, the function handles it gracefully.
+func TestRequestWitnesses_PartialFailureNoPanic(t *testing.T) {
+	ctrl := gomock.NewController(t)
+	defer ctrl.Finish()
+
+	hashToRequest := common.Hash{123}
+	mockWitPeer := NewMockWitnessPeer(ctrl)
+	p := &ethPeer{
+		Peer:    eth.NewPeer(1, p2p.NewPeer(enode.ID{0x01, 0x02}, "test-peer", []p2p.Cap{}), nil, nil),
+		witPeer: &witPeer{Peer: mockWitPeer},
+	}
+	dlCh := make(chan *eth.Response, 1)
+
+	mockWitPeer.EXPECT().Log().Return(log.New()).AnyTimes()
+
+	// Mock RequestWitness to send malformed response (wrong type).
+	mockWitPeer.
+		EXPECT().
+		RequestWitness(gomock.Any(), gomock.Any()).
+		DoAndReturn(func(wpr []wit.WitnessPageRequest, ch chan *wit.Response) (*wit.Request, error) {
+			go func() {
+				// Send response with wrong type (not WitnessPacketRLPPacket).
+				ch <- &wit.Response{
+					Res:  "invalid_response_type", // Wrong type
+					Done: make(chan error, 1),
+				}
+			}()
+			return &wit.Request{}, nil
+		}).
+		AnyTimes()
+
+	// Call RequestWitnesses.
+	req, err := p.RequestWitnesses([]common.Hash{hashToRequest}, dlCh)
+	assert.NoError(t, err)
+	assert.NotNil(t, req)
+
+	// Wait for response - should get empty response due to processing failure.
+	select {
+	case response := <-dlCh:
+		assert.NotNil(t, response)
+		witnesses, ok := response.Res.([]*stateless.Witness)
+		assert.True(t, ok, "should receive []*stateless.Witness type even on processing failure")
+		assert.Equal(t, 0, len(witnesses), "should receive empty witness slice when processing fails")
+
+	case <-time.After(2 * time.Second):
+		t.Fatal("timed out waiting for response")
+	}
+}
```
