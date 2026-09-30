# [?] les: fix panic (#20013)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-08-27
Source: https://github.com/celo-org/celo-blockchain/commit/396f1dd87b91cc08a1db08aaa2b901a47b69d26f
Type: security-commit

## Details
les: fix panic (#20013)

## Patch
### les/server_handler.go
```diff
@@ -583,15 +583,14 @@ func (h *serverHandler) handleMsg(p *peer, wg *sync.WaitGroup) error {
 					}
 					// Look up the root hash belonging to the request
 					var (
-						number *uint64
 						header *types.Header
 						trie   state.Trie
 					)
 					if request.BHash != lastBHash {
 						root, lastBHash = common.Hash{}, request.BHash
 
 						if header = h.blockchain.GetHeaderByHash(request.BHash); header == nil {
-							p.Log().Warn("Failed to retrieve header for proof", "block", *number, "hash", request.BHash)
+							p.Log().Warn("Failed to retrieve header for proof", "hash", request.BHash)
 							atomic.AddUint32(&p.invalidCount, 1)
 							continue
 						}
```
