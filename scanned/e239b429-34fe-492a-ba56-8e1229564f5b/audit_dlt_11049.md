# [?] prevent nil chainView panic

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2026-02-17
Source: https://github.com/OffchainLabs/go-ethereum/commit/0e42d21aac290fe37cf1708b2b8f875c021de093
Type: security-commit

## Details
prevent nil chainView panic

## Patch
### eth/backend.go
```diff
@@ -500,6 +500,11 @@ func (s *Ethereum) updateFilterMapsHeads() {
 		if head == nil || newHead.Hash() != head.Hash() {
 			head = newHead
 			chainView := s.newChainView(head)
+			// passing nil chainView to FilterMaps.SetTarget triggers a panic
+			// newChainView can return nil not only when head == nil but also when ChainView.extendNonCanonical returns false
+			if chainView == nil {
+				return
+			}
 			historyCutoff, _ := s.blockchain.HistoryPruningCutoff()
 			var finalBlock uint64
 			if fb := s.blockchain.CurrentFinalBlock(); fb != nil {
```
