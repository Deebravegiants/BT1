# [?] catchup: fix potential nil dereferencing (#2420)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-07-01
Source: https://github.com/algorand/go-algorand/commit/fc52ab9b886df7a7f76530bbe68e19a4ee08ce52
Type: security-commit

## Details
catchup: fix potential nil dereferencing (#2420)

The handing for returned peer was incorrect in case the getPeerErr is non-nil, as we would attempt to dereference the nil pointer.

## Patch
### catchup/catchpointService.go
```diff
@@ -282,11 +282,11 @@ func (cs *CatchpointCatchupService) processStageLedgerDownload() (err error) {
 			return cs.abort(fmt.Errorf("processStageLedgerDownload failed to reset staging balances : %v", err))
 		}
 		psp, err := peerSelector.getNextPeer()
-		peer := psp.Peer
 		if err != nil {
 			err = fmt.Errorf("processStageLedgerDownload: catchpoint catchup was unable to obtain a list of peers to retrieve the catchpoint file from")
 			return cs.abort(err)
 		}
+		peer := psp.Peer
 		err = ledgerFetcher.downloadLedger(cs.ctx, peer, round)
 		if err == nil {
 			err = cs.ledgerAccessor.BuildMerkleTrie(cs.ctx, cs.updateVerifiedAccounts)
@@ -584,11 +584,11 @@ func (cs *CatchpointCatchupService) processStageBlocksDownload() (err error) {
 // If the method return a nil block, the caller is expected to retry the operation, increasing the retry counter as needed.
 func (cs *CatchpointCatchupService) fetchBlock(round basics.Round, retryCount uint64) (blk *bookkeeping.Block, downloadDuration time.Duration, psp *peerSelectorPeer, stop bool, err error) {
 	psp, err = cs.blocksDownloadPeerSelector.getNextPeer()
-	peer := psp.Peer
 	if err != nil {
 		err = fmt.Errorf("fetchBlock: unable to obtain a list of peers to retrieve the latest block from")
 		return nil, time.Duration(0), psp, true, cs.abort(err)
 	}
+	peer := psp.Peer
 
 	httpPeer, validPeer := peer.(network.HTTPPeer)
 	if !validPeer {
```

### catchup/service.go
```diff
@@ -209,11 +209,11 @@ func (s *Service) fetchAndWrite(r basics.Round, prevFetchCompleteChan chan bool,
 		}
 
 		psp, getPeerErr := peerSelector.getNextPeer()
-		peer := psp.Peer
 		if getPeerErr != nil {
 			s.log.Debugf("fetchAndWrite: was unable to obtain a peer to retrieve the block from")
 			break
 		}
+		peer := psp.Peer
 
 		// Try to fetch, timing out after retryInterval
 		block, cert, blockDownloadDuration, err := s.innerFetch(r, peer)
@@ -604,12 +604,12 @@ func (s *Service) fetchRound(cert agreement.Certificate, verifier *agreement.Asy
 	peerSelector := s.createPeerSelector(false)
 	for s.ledger.LastRound() < cert.Round {
 		psp, getPeerErr := peerSelector.getNextPeer()
-		peer := psp.Peer
 		if getPeerErr != nil {
 			s.log.Debugf("fetchRound: was unable to obtain a peer to retrieve the block from")
 			s.net.RequestConnectOutgoing(true, s.ctx.Done())
 			continue
 		}
+		peer := psp.Peer
 
 		// Ask the fetcher to get the block somehow
 		block, fetchedCert, _, err := s.innerFetch(cert.Round, peer)
```
