# [?] fix(comm): deadlock when communicator exit

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-05-03
Source: https://github.com/vechain/thor/commit/c68bdaa6f0eefb19fb6e8bdfd8eb8be5804fd172
Type: security-commit

## Details
fix(comm): deadlock when communicator exit

## Patch
### comm/handle_request.go
```diff
@@ -70,7 +70,12 @@ func (c *Communicator) handleRequest(peer *p2psrv.Peer, msg *p2p.Msg) (interface
 		if s := c.sessionSet.Find(peer.ID()); s != nil {
 			s.MarkBlock(req.ID)
 		}
-		c.goes.Go(func() { c.announceCh <- &announce{req.ID, peer} })
+		c.goes.Go(func() {
+			select {
+			case c.announceCh <- &announce{req.ID, peer}:
+			case <-c.ctx.Done():
+			}
+		})
 		return &struct{}{}, nil
 	case proto.MsgGetBlockByID:
 		var req proto.ReqGetBlockByID
```
