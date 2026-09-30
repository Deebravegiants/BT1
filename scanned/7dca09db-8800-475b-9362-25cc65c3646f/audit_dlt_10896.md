# [?] fix: panic on block syncing

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-06-11
Source: https://github.com/vechain/thor/commit/63428917cd1c844d971a71ff67d152abdb220357
Type: security-commit

## Details
fix: panic on block syncing

## Patch
### comm/sync.go
```diff
@@ -8,7 +8,6 @@ package comm
 import (
 	"context"
 	"fmt"
-	"sync/atomic"
 
 	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/pkg/errors"
@@ -26,23 +25,26 @@ func (c *Communicator) sync(peer *Peer, headNum uint32, handler HandleBlockStrea
 }
 
 func (c *Communicator) download(peer *Peer, fromNum uint32, handler HandleBlockStream) error {
+
+	// it's important to set cap to 2
+	errCh := make(chan error, 2)
+
 	ctx, cancel := context.WithCancel(c.ctx)
-	var errValue atomic.Value
 	blockCh := make(chan *block.Block, 32)
 
 	var goes co.Goes
 	goes.Go(func() {
 		defer cancel()
 		if err := handler(ctx, blockCh); err != nil {
-			errValue.Store(err)
+			errCh <- err
 		}
 	})
 	goes.Go(func() {
 		defer close(blockCh)
 		for {
 			result, err := proto.GetBlocksFromNumber(ctx, peer, fromNum)
 			if err != nil {
-				errValue.Store(err)
+				errCh <- err
 				return
 			}
 			if len(result) == 0 {
@@ -52,15 +54,15 @@ func (c *Communicator) download(peer *Peer, fromNum uint32, handler HandleBlockS
 			for _, raw := range result {
 				var blk block.Block
 				if err := rlp.DecodeBytes(raw, &blk); err != nil {
-					errValue.Store(errors.Wrap(err, "invalid block"))
+					errCh <- errors.Wrap(err, "invalid block")
 					return
 				}
 				if _, err := blk.Header().Signer(); err != nil {
-					errValue.Store(errors.Wrap(err, "invalid block"))
+					errCh <- errors.Wrap(err, "invalid block")
 					return
 				}
 				if blk.Header().Number() != fromNum {
-					errValue.Store(errors.New("broken sequence"))
+					errCh <- errors.New("broken sequence")
 					return
 				}
 				peer.MarkBlock(blk.Header().ID())
@@ -75,10 +77,13 @@ func (c *Communicator) download(peer *Peer, fromNum uint32, handler HandleBlockS
 		}
 	})
 	goes.Wait()
-	if err := errValue.Load(); err != nil {
-		return err.(error)
+
+	select {
+	case err := <-errCh:
+		return err
+	default:
+		return nil
 	}
-	return nil
 }
 
 func (c *Communicator) findCommonAncestor(peer *Peer, headNum uint32) (uint32, error) {
```
