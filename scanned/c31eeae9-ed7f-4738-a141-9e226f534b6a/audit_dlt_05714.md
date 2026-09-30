# [?] splice: Test fix for test crash splice

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-05-14
Source: https://github.com/ElementsProject/lightning/commit/b76c0c1d376b3667e5fd758dee9ddd8f07c9e8a9
Type: security-commit

## Details
splice: Test fix for test crash splice

Fix a typo where the commit sig message ordering was not handled correctly for the first element.

We need to use msg_batch[0] to get the first post-sorted result instead of the original msg.

Changelog-None

## Patch
### channeld/channeld.c
```diff
@@ -2369,11 +2369,11 @@ static struct commitsig_info *handle_peer_commit_sig_batch(struct peer *peer,
 	status_debug("Sorting the msg_batch of tal_count %d, batch_size: %d", (int)tal_count(msg_batch), (int)batch_size);
 	asort(msg_batch, tal_count(msg_batch), commit_cmp, peer);
 
-	return handle_peer_commit_sig(peer, msg, commit_index, remote_funding,
-				      changed_htlcs, splice_amnt,
-				      remote_splice_amnt, local_index,
-				      local_per_commit, allow_empty_commit,
-				      msg_batch);
+	return handle_peer_commit_sig(peer, msg_batch[0], commit_index,
+				      remote_funding, changed_htlcs,
+				      splice_amnt, remote_splice_amnt,
+				      local_index, local_per_commit,
+				      allow_empty_commit, msg_batch);
 }
 
 /* Pops the penalty base for the given commitnum from our internal list. There
```
