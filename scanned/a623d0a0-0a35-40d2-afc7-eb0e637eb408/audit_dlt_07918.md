# [?] txpool: fix a potential crash issue in shutdown; (#1951)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2023-10-30
Source: https://github.com/bnb-chain/bsc/commit/0d9151eb8f4e85d89a8c66f2f3c012693c32cfef
Type: security-commit

## Details
txpool: fix a potential crash issue in shutdown; (#1951)

## Patch
### core/txpool/txpool.go
```diff
@@ -319,11 +319,11 @@ func (p *TxPool) Pending(enforceTips bool) map[common.Address][]*LazyTransaction
 // SubscribeNewTxsEvent registers a subscription of NewTxsEvent and starts sending
 // events to the given channel.
 func (p *TxPool) SubscribeNewTxsEvent(ch chan<- core.NewTxsEvent) event.Subscription {
-	subs := make([]event.Subscription, len(p.subpools))
-	for i, subpool := range p.subpools {
+	subs := make([]event.Subscription, 0, len(p.subpools))
+	for _, subpool := range p.subpools {
 		sub := subpool.SubscribeTransactions(ch)
 		if sub != nil { // sub will be nil when subpool have been shut down
-			subs[i] = sub
+			subs = append(subs, sub)
 		}
 	}
 	return p.subs.Track(event.JoinSubscriptions(subs...))
@@ -332,11 +332,11 @@ func (p *TxPool) SubscribeNewTxsEvent(ch chan<- core.NewTxsEvent) event.Subscrip
 // SubscribeNewTxsEvent registers a subscription of NewTxsEvent and starts sending
 // events to the given channel.
 func (p *TxPool) SubscribeReannoTxsEvent(ch chan<- core.ReannoTxsEvent) event.Subscription {
-	subs := make([]event.Subscription, len(p.subpools))
-	for i, subpool := range p.subpools {
+	subs := make([]event.Subscription, 0, len(p.subpools))
+	for _, subpool := range p.subpools {
 		sub := subpool.SubscribeReannoTxsEvent(ch)
 		if sub != nil { // sub will be nil when subpool have been shut down
-			subs[i] = sub
+			subs = append(subs, sub)
 		}
 	}
 	return p.subs.Track(event.JoinSubscriptions(subs...))
```
