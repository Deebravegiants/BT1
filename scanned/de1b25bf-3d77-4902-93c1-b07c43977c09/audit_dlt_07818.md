# [?] Fix Overflow Bugs Introduced (#7579)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2020-10-20
Source: https://github.com/OffchainLabs/prysm/commit/81b553a00a550efe9b35003060b72d1e0bbc0c83
Type: security-commit

## Details
Fix Overflow Bugs Introduced (#7579)

## Patch
### beacon-chain/powchain/service.go
```diff
@@ -649,7 +649,6 @@ func (s *Service) initPOWService() {
 				s.retryETH1Node(err)
 				continue
 			}
-			s.cacheHeadersForEth1DataVote(ctx)
 
 			s.latestEth1Data.BlockHeight = header.Number.Uint64()
 			s.latestEth1Data.BlockHash = header.Hash().Bytes()
@@ -660,6 +659,8 @@ func (s *Service) initPOWService() {
 				s.retryETH1Node(err)
 				continue
 			}
+			// Cache eth1 headers from our voting period.
+			s.cacheHeadersForEth1DataVote(ctx)
 			return
 		}
 	}
@@ -739,12 +740,10 @@ func (s *Service) cacheHeadersForEth1DataVote(ctx context.Context) {
 		log.Errorf("Unable to fetch height of follow block: %v", err)
 	}
 
-	var start uint64
 	// We fetch twice the number of headers just to be safe.
-	if end-2*blocksPerVotingPeriod >= 0 {
+	start := uint64(0)
+	if end >= 2*blocksPerVotingPeriod {
 		start = end - 2*blocksPerVotingPeriod
-	} else {
-		start = 0
 	}
 	// We call batchRequestHeaders for its header caching side-effect, so we don't need the return value.
 	_, err = s.batchRequestHeaders(start, end)
```
