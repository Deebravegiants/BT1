# [?] les: fixed transaction sending deadlock (#3568)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-01-16
Source: https://github.com/scroll-tech/go-ethereum/commit/0fa9a8929c8a55d1b624479cead2bb960ada7cfd
Type: security-commit

## Details
les: fixed transaction sending deadlock (#3568)

## Patch
### les/txrelay.go
```diff
@@ -110,7 +110,6 @@ func (self *LesTxRelay) send(txs types.Transactions, count int) {
 	for p, list := range sendTo {
 		cost := p.GetRequestCost(SendTxMsg, len(list))
 		go func(p *peer, list types.Transactions, cost uint64) {
-			p.fcServer.SendRequest(0, cost)
 			p.SendTxs(cost, list)
 		}(p, list, cost)
 	}
```
