# [?] Merge pull request #10035 from ziggie1984/fix-switch-deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-07-04
Source: https://github.com/lightningnetwork/lnd/commit/ff32e90d1dea9de9d133c475f16a08375934a004
Type: security-commit

## Details
Merge pull request #10035 from ziggie1984/fix-switch-deadlock

fix switch deadlock

## Patch
### docs/release-notes/release-notes-0.19.2.md
```diff
@@ -37,6 +37,8 @@
   could lead to a memory issues due to a goroutine leak in the peer/gossiper
   code.
 
+- [Fixed](https://github.com/lightningnetwork/lnd/pull/10035) a deadlock (writer starvation) in the switch.
+
 # New Features
 
 ## Functional Enhancements
```

### htlcswitch/switch.go
```diff
@@ -880,7 +880,6 @@ func (s *Switch) getLocalLink(pkt *htlcPacket, htlc *lnwire.UpdateAddHTLC) (
 	// Try to find links by node destination.
 	s.indexMtx.RLock()
 	link, err := s.getLinkByShortID(pkt.outgoingChanID)
-	defer s.indexMtx.RUnlock()
 	if err != nil {
 		// If the link was not found for the outgoingChanID, an outside
 		// subsystem may be using the confirmed SCID of a zero-conf
@@ -892,6 +891,7 @@ func (s *Switch) getLocalLink(pkt *htlcPacket, htlc *lnwire.UpdateAddHTLC) (
 		// do that upon receiving the packet.
 		baseScid, ok := s.baseIndex[pkt.outgoingChanID]
 		if !ok {
+			s.indexMtx.RUnlock()
 			log.Errorf("Link %v not found", pkt.outgoingChanID)
 			return nil, NewLinkError(&lnwire.FailUnknownNextPeer{})
 		}
@@ -900,10 +900,15 @@ func (s *Switch) getLocalLink(pkt *htlcPacket, htlc *lnwire.UpdateAddHTLC) (
 		// link.
 		link, err = s.getLinkByShortID(baseScid)
 		if err != nil {
+			s.indexMtx.RUnlock()
 			log.Errorf("Link %v not found", baseScid)
 			return nil, NewLinkError(&lnwire.FailUnknownNextPeer{})
 		}
 	}
+	// We finished looking up the indexes, so we can unlock the mutex before
+	// performing the link operations which might also acquire the lock
+	// in case e.g. failAliasUpdate is called.
+	s.indexMtx.RUnlock()
 
 	if !link.EligibleToForward() {
 		log.Errorf("Link %v is not available to forward",
@@ -928,6 +933,7 @@ func (s *Switch) getLocalLink(pkt *htlcPacket, htlc *lnwire.UpdateAddHTLC) (
 			"satisfied", pkt.outgoingChanID)
 		return nil, htlcErr
 	}
+
 	return link, nil
 }
 
```
