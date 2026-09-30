# [?] channeldb: fix race condition in link node pruning

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-12-22
Source: https://github.com/lightningnetwork/lnd/commit/51f3c6f5286f5c6bfbc906b1861c647e5fcba61f
Type: security-commit

## Details
channeldb: fix race condition in link node pruning

This commit fixes a critical race condition in MarkChanFullyClosed and
pruneLinkNode where link nodes could be incorrectly deleted despite
having pending or open channels.

The race occurred because the check for open channels and the link node
deletion happened in separate database transactions:

  Thread A: TX1 checks open channels → [] (empty)
  Thread A: TX1 commits
  Thread B: Opens new channel with same peer
  Thread A: TX2 deletes link node (using stale data)
  Result: Link node deleted despite pending channel existing

This creates a TOCTOU (time-of-check to time-of-use) vulnerability where
database state changes between reading the channel count and deleting
the node.

Fix for MarkChanFullyClosed:
- Move link node deletion into the same transaction as the channel
  closing check, making the check-and-delete operation atomic

Fix for pruneLinkNode:
- Add double-check within the write transaction to verify no channels
  were opened since the caller's initial check
- Maintains performance by keeping early return for common case
- Prevents deletion if channels exist at delete time

This ensures the invariant: "link node exists iff channels exist"
is never violated, preventing database corruption and potential
connection issues.

## Patch
### channeldb/db.go
```diff
@@ -1363,11 +1363,7 @@ func (c *ChannelStateDB) FetchClosedChannelForID(cid lnwire.ChannelID) (
 // the pending funds in a channel that has been forcibly closed have been
 // swept.
 func (c *ChannelStateDB) MarkChanFullyClosed(chanPoint *wire.OutPoint) error {
-	var (
-		openChannels  []*OpenChannel
-		pruneLinkNode *btcec.PublicKey
-	)
-	err := kvdb.Update(c.backend, func(tx kvdb.RwTx) error {
+	return kvdb.Update(c.backend, func(tx kvdb.RwTx) error {
 		var b bytes.Buffer
 		if err := graphdb.WriteOutpoint(&b, chanPoint); err != nil {
 			return err
@@ -1413,44 +1409,72 @@ func (c *ChannelStateDB) MarkChanFullyClosed(chanPoint *wire.OutPoint) error {
 		// other open channels with this peer. If we don't we'll
 		// garbage collect it to ensure we don't establish persistent
 		// connections to peers without open channels.
-		pruneLinkNode = chanSummary.RemotePub
-		openChannels, err = c.fetchOpenChannels(
-			tx, pruneLinkNode,
-		)
+		remotePub := chanSummary.RemotePub
+		openChannels, err := c.fetchOpenChannels(tx, remotePub)
 		if err != nil {
 			return fmt.Errorf("unable to fetch open channels for "+
 				"peer %x: %v",
-				pruneLinkNode.SerializeCompressed(), err)
+				remotePub.SerializeCompressed(), err)
 		}
 
-		return nil
-	}, func() {
-		openChannels = nil
-		pruneLinkNode = nil
-	})
-	if err != nil {
-		return err
-	}
+		if len(openChannels) > 0 {
+			return nil
+		}
+
+		// If there are no open channels with this peer, prune the
+		// link node. We do this within the same transaction to avoid
+		// a race condition where a new channel could be opened
+		// between this check and the deletion.
+		log.Infof("Pruning link node %x with zero open "+
+			"channels from database",
+			remotePub.SerializeCompressed())
 
-	// Decide whether we want to remove the link node, based upon the number
-	// of still open channels.
-	return c.pruneLinkNode(openChannels, pruneLinkNode)
+		err = deleteLinkNode(tx, remotePub)
+		if err != nil {
+			return fmt.Errorf("unable to delete link "+
+				"node: %w", err)
+		}
+
+		return nil
+	}, func() {})
 }
 
 // pruneLinkNode determines whether we should garbage collect a link node from
-// the database due to no longer having any open channels with it. If there are
-// any left, then this acts as a no-op.
-func (c *ChannelStateDB) pruneLinkNode(openChannels []*OpenChannel,
-	remotePub *btcec.PublicKey) error {
+// the database due to no longer having any open channels with it.
+//
+// NOTE: This function should be called after an initial check shows no open
+// channels exist. It will double-check within a write transaction to avoid a
+// race condition where a channel could be opened between the initial check
+// and the deletion.
+func (c *ChannelStateDB) pruneLinkNode(remotePub *btcec.PublicKey) error {
+	return kvdb.Update(c.backend, func(tx kvdb.RwTx) error {
+		// Double-check for open channels to avoid deleting a link node
+		// if a channel was opened since the caller's initial check.
+		//
+		// NOTE: This avoids a race condition where a channel could be
+		// opened between the initial check and the deletion.
+		openChannels, err := c.fetchOpenChannels(tx, remotePub)
+		if err != nil {
+			return err
+		}
 
-	if len(openChannels) > 0 {
-		return nil
-	}
+		// If channels exist now, don't prune.
+		if len(openChannels) > 0 {
+			return nil
+		}
 
-	log.Infof("Pruning link node %x with zero open channels from database",
-		remotePub.SerializeCompressed())
+		// No open channels, safe to prune the link node.
+		log.Infof("Pruning link node %x with zero open channels "+
+			"from database",
+			remotePub.SerializeCompressed())
 
-	return c.linkNodeDB.DeleteLinkNode(remotePub)
+		err = deleteLinkNode(tx, remotePub)
+		if err != nil {
+			return fmt.Errorf("unable to prune link node: %w", err)
+		}
+
+		return nil
+	}, func() {})
 }
 
 // PruneLinkNodes attempts to prune all link nodes found within the database
@@ -1479,7 +1503,11 @@ func (c *ChannelStateDB) PruneLinkNodes() error {
 			return err
 		}
 
-		err = c.pruneLinkNode(openChannels, linkNode.IdentityPub)
+		if len(openChannels) > 0 {
+			continue
+		}
+
+		err = c.pruneLinkNode(linkNode.IdentityPub)
 		if err != nil {
 			return err
 		}
```
