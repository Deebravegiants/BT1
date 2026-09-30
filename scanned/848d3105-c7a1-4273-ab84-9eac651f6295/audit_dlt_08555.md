# [?] Fix a rare data race condition. (#1017)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2020-05-11
Source: https://github.com/algorand/go-algorand/commit/9b88685b3a62a21c26581a4f26f52cc7fec0cdfb
Type: security-commit

## Details
Fix a rare data race condition. (#1017)

## Patch
### agreement/demux.go
```diff
@@ -74,16 +74,15 @@ func makeDemux(net Network, ledger LedgerReader, validator BlockValidator, voteV
 	d.crypto = makeCryptoVerifier(ledger, validator, voteVerifier, log)
 	d.log = log
 	d.ledger = ledger
+	d.queue = make([]<-chan externalEvent, 0)
+	d.processingMonitor = processingMonitor
 
 	tokenizerCtx, cancelTokenizers := context.WithCancel(context.Background())
 	d.rawVotes = d.tokenizeMessages(tokenizerCtx, net, protocol.AgreementVoteTag, decodeVote)
 	d.rawProposals = d.tokenizeMessages(tokenizerCtx, net, protocol.ProposalPayloadTag, decodeProposal)
 	d.rawBundles = d.tokenizeMessages(tokenizerCtx, net, protocol.VoteBundleTag, decodeBundle)
 	d.cancelTokenizers = cancelTokenizers
 
-	d.queue = make([]<-chan externalEvent, 0)
-	d.processingMonitor = processingMonitor
-
 	return d
 }
 
```
