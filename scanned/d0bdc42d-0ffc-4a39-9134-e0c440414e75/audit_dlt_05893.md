# [?] Fixed an error in building the plan for the endorsement. Periodically, the `endorse retry - org3 fail & 1 org2 peer fail - requires 2 from org1` test 

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2026-04-23
Source: https://github.com/hyperledger/fabric/commit/2190a1c8e0677cceed8a6ccc1604d793095fc481
Type: security-commit

## Details
Fixed an error in building the plan for the endorsement. Periodically, the `endorse retry - org3 fail & 1 org2 peer fail - requires 2 from org1` test fails with an error. I figured it out and added the TestMultiLayoutFailures1 test, which crashes in the old version of the code. (#5456)

Signed-off-by: Fedor Partanskiy <fredprtnsk@gmail.com>

## Patch
### internal/pkg/gateway/endorse.go
```diff
@@ -80,28 +80,33 @@ func (gs *Server) Endorse(ctx context.Context, request *gp.EndorseRequest) (*gp.
 			break
 		}
 		// send to all the endorsers
-		waitCh := make(chan bool, len(endorsers))
+		waitCh := make(chan string, len(endorsers))
 		for _, e := range endorsers {
 			go func(e *endorser) {
+				var g string
 				for e != nil {
 					if gs.processProposal(ctx, plan, e, signedProposal, logger) {
 						break
 					}
-					e = plan.nextPeerInGroup(e)
+					e, g = plan.nextPeerInGroup(e)
 				}
-				waitCh <- true
+				waitCh <- g
 			}(e)
 		}
+
+		groups := make([]string, 0, len(endorsers))
 		for range endorsers {
 			select {
-			case <-waitCh:
+			case group := <-waitCh:
 				// Endorser completedLayout normally
+				groups = append(groups, group)
 			case <-ctx.Done():
 				logger.Warnw("Endorse call timed out while collecting endorsements", "numEndorsers", len(endorsers))
 				return nil, newRpcError(codes.DeadlineExceeded, "endorsement timeout expired while collecting endorsements")
 			}
 		}
 
+		plan.abandonGroupRemoveLayouts(groups...)
 	}
 
 	if plan.completedLayout == nil {
@@ -211,8 +216,10 @@ func (gs *Server) planFromFirstEndorser(ctx context.Context, channel string, cha
 				if remove {
 					gs.registry.removeEndorser(firstEndorser)
 				}
-				firstEndorser = plan.nextPeerInGroup(firstEndorser)
+				var group string
+				firstEndorser, group = plan.nextPeerInGroup(firstEndorser)
 				firstResponse = nil
+				plan.abandonGroupRemoveLayouts(group)
 			}
 		}()
 		select {
```

### internal/pkg/gateway/endorsement.go
```diff
@@ -159,7 +159,7 @@ func (p *plan) processEndorsement(endorser *endorser, response *peer.ProposalRes
 
 // Invoke nextPeerInGroup if an endorsement fails for the given endorser.
 // Returns the next endorser in the same group as given endorser with which to retry the proposal, or nil if there are no more.
-func (p *plan) nextPeerInGroup(endorser *endorser) *endorser {
+func (p *plan) nextPeerInGroup(endorser *endorser) (*endorser, string) {
 	p.planLock.Lock()
 	defer p.planLock.Unlock()
 
@@ -169,24 +169,34 @@ func (p *plan) nextPeerInGroup(endorser *endorser) *endorser {
 	if len(p.groupEndorsers[group]) > 0 {
 		next := p.groupEndorsers[group][0]
 		p.groupEndorsers[group] = p.groupEndorsers[group][1:]
-		return next
+		return next, ""
 	}
 
+	return nil, group
+}
+
+func (p *plan) abandonGroupRemoveLayouts(groups ...string) {
 	// There are no more peers in this group, so will abandon this group entirely and remove all layouts that use it
 	// Clearly the current layout was using it, so remove that
 	// To avoid memory re-allocations, mark them as nil
 	for i := p.nextLayout; i < len(p.layouts); i++ {
-		layout := p.layouts[i]
-		if layout != nil {
+		for _, group := range groups {
+			if group == "" {
+				continue
+			}
+
+			layout := p.layouts[i]
+			if layout == nil {
+				continue
+			}
+
 			if _, exists := layout.required[group]; exists {
 				p.layouts[i] = nil
 			}
 		}
 	}
 	// continue with the next layout
 	p.nextLayout++
-
-	return nil
 }
 
 func (p *plan) addError(detail proto.Message) {
```

### internal/pkg/gateway/endorsement_test.go
```diff
@@ -64,15 +64,15 @@ func TestSingleLayoutRetry(t *testing.T) {
 	response2 := &peer.ProposalResponse{Payload: []byte("p"), Endorsement: &peer.Endorsement{Endorser: []byte("e2")}}
 	response3 := &peer.ProposalResponse{Payload: []byte("p"), Endorsement: &peer.Endorsement{Endorser: []byte("e3")}}
 
-	retry := plan.nextPeerInGroup(localhostMock)
+	retry, _ := plan.nextPeerInGroup(localhostMock)
 	require.Equal(t, peer1Mock, retry)
 	success := plan.processEndorsement(retry, response1)
 	require.True(t, success)
 	require.Nil(t, plan.completedLayout)
 	success = plan.processEndorsement(peer2Mock, response2)
 	require.True(t, success)
 	require.Nil(t, plan.completedLayout)
-	retry = plan.nextPeerInGroup(peer3Mock)
+	retry, _ = plan.nextPeerInGroup(peer3Mock)
 	require.Equal(t, peer4Mock, retry)
 	success = plan.processEndorsement(retry, response3)
 	require.True(t, success)
@@ -103,16 +103,17 @@ func TestMultiLayoutRetry(t *testing.T) {
 	response2 := &peer.ProposalResponse{Payload: []byte("p"), Endorsement: &peer.Endorsement{Endorser: []byte("e2")}}
 
 	// localhost (g1) fails, returns peer1 to retry
-	retry := plan.nextPeerInGroup(localhostMock)
+	retry, _ := plan.nextPeerInGroup(localhostMock)
 	require.Equal(t, peer1Mock, retry)
 
 	// peer2 (g2) succeeds
 	success := plan.processEndorsement(peer2Mock, response1)
 	require.True(t, success)
 
 	// peer1 (g1) also fails - returns nil, since no more peers in g1
-	retry = plan.nextPeerInGroup(retry)
+	retry, group := plan.nextPeerInGroup(retry)
 	require.Nil(t, retry)
+	plan.abandonGroupRemoveLayouts(group)
 
 	// get endorsers for next layout - should be layout 3 because second layout also required g1
 	endorsers = plan.endorsers()
@@ -153,11 +154,11 @@ func TestMultiLayoutFailures(t *testing.T) {
 	require.True(t, success)
 
 	// peer2 (g2) fails - returns peer3 to retry
-	retry := plan.nextPeerInGroup(peer2Mock)
+	retry, _ := plan.nextPeerInGroup(peer2Mock)
 	require.Equal(t, peer3Mock, retry)
 
 	// peer4 (g3) also fails - returns nil, since no more peers in g3
-	g3retry := plan.nextPeerInGroup(peer4Mock)
+	g3retry, _ := plan.nextPeerInGroup(peer4Mock)
 	require.Nil(t, g3retry)
 
 	// retry g2 - succeeds
@@ -172,14 +173,57 @@ func TestMultiLayoutFailures(t *testing.T) {
 	require.Equal(t, peer1Mock, endorsers[0])
 
 	// this one fails too
-	retry = plan.nextPeerInGroup(peer1Mock)
+	retry, _ = plan.nextPeerInGroup(peer1Mock)
 	// no more in this group
 	require.Nil(t, retry)
 	endorsers = plan.endorsers()
 	// we've run out of layouts - failed to endorse!
 	require.Nil(t, endorsers)
 }
 
+func TestMultiLayoutFailures1(t *testing.T) {
+	layouts := []*layout{
+		{required: map[string]int{"g1": 1, "g2": 2}},
+		{required: map[string]int{"g1": 2, "g2": 1}},
+		{required: map[string]int{"g1": 1, "g2": 1, "g3": 1}},
+	}
+	groupEndorsers := map[string][]*endorser{
+		"g1": {localhostMock, peer1Mock},
+		"g2": {peer2Mock, peer3Mock},
+		"g3": {peer4Mock},
+	}
+	plan := newPlan(layouts, groupEndorsers)
+	require.Equal(t, plan.size, 5) // total number of endorsers in all layouts
+
+	endorsers := plan.endorsers() // first layout
+	require.Len(t, endorsers, 3)
+	require.ElementsMatch(t, endorsers, []*endorser{localhostMock, peer2Mock, peer3Mock})
+
+	response1 := &peer.ProposalResponse{Payload: []byte("p"), Endorsement: &peer.Endorsement{Endorser: []byte("e1")}}
+	response2 := &peer.ProposalResponse{Payload: []byte("p"), Endorsement: &peer.Endorsement{Endorser: []byte("e2")}}
+
+	// localhost (g1) succeeds
+	success := plan.processEndorsement(localhostMock, response1)
+	require.True(t, success)
+
+	// peer2 (g2) fails - returns nil to retry
+	retry, group := plan.nextPeerInGroup(peer2Mock)
+	require.Nil(t, retry)
+
+	// peer3 (g2) succeeds
+	success = plan.processEndorsement(peer3Mock, response2)
+	require.True(t, success)
+
+	plan.abandonGroupRemoveLayouts(group)
+
+	// nothing more to try in this layout - get endorsers for next layout
+	// layout 2 requires a second endorsement from g2, but all g2 peers have been tried - only 1 succeeded
+	// should return layout 3 which requires a second endorsement from g1
+	endorsers = plan.endorsers()
+	require.Len(t, endorsers, 1)
+	require.Equal(t, peer1Mock, endorsers[0])
+}
+
 func TestMultiPlan(t *testing.T) {
 	layouts1 := []*layout{
 		{required: map[string]int{"g1": 1}},
```

### internal/pkg/gateway/evaluate.go
```diff
@@ -78,7 +78,10 @@ func (gs *Server) Evaluate(ctx context.Context, request *gp.EvaluateRequest) (*g
 					gs.registry.removeEndorser(endorser)
 				}
 				if retry {
-					endorser = plan.nextPeerInGroup(endorser)
+					var group string
+					endorser, group = plan.nextPeerInGroup(endorser)
+					plan.abandonGroupRemoveLayouts(group)
+
 				} else {
 					done <- newRpcError(code, "evaluate call to endorser returned error: "+message, errDetails...)
 				}
```
