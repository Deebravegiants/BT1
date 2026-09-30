# [?] fix(comm): crash when received new tx

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-05-04
Source: https://github.com/vechain/thor/commit/e9d9cc67b91a01b449d61a323c065caf0e7b1a8f
Type: security-commit

## Details
fix(comm): crash when received new tx

## Patch
### comm/handle_request.go
```diff
@@ -41,7 +41,7 @@ func (c *Communicator) handleRequest(peer *p2psrv.Peer, msg *p2p.Msg) (interface
 		if s := c.sessionSet.Find(peer.ID()); s != nil {
 			s.MarkTransaction(req.Tx.ID())
 		}
-		c.goes.Go(func() { c.newTxFeed.Send(req.Tx) })
+		c.goes.Go(func() { c.newTxFeed.Send(&NewTransactionEvent{req.Tx}) })
 		return &struct{}{}, nil
 	case proto.MsgNewBlock:
 		var req proto.ReqNewBlock
```
