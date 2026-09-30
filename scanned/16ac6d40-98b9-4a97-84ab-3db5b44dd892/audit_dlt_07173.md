# [?] connectd: fix double-free crash on connection timeout.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-10-14
Source: https://github.com/ElementsProject/lightning/commit/4e6bac6d3678183ea4dbee5fb381c4f19a66deda
Type: security-commit

## Details
connectd: fix double-free crash on connection timeout.

tmpctx may not get cleaned immediately, so the timeout (a child of
the struct early_peer at this point) can still outlast the conn.
Do the clearer thing, and explicitly free the timeout.

Changelog-Fixed: connectd: crash on erroneous timeout.
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### connectd/peer_exchange_initmsg.c
```diff
@@ -31,6 +31,9 @@ struct early_peer {
 	enum is_websocket is_websocket;
 
 	bool incoming;
+
+	/* Timeout in case it takes too long */
+	struct oneshot *timeout;
 };
 
 static bool contains_common_chain(struct bitcoin_blkid *chains)
@@ -128,6 +131,9 @@ static struct io_plan *peer_init_received(struct io_conn *conn,
 	 * window where it was: combine the two. */
 	features = featurebits_or(tmpctx, take(features), globalfeatures);
 
+	/* No longer timing out! */
+	tal_free(peer->timeout);
+
 	/* We can dispose of peer after next call. */
 	tal_steal(tmpctx, peer);
 
@@ -206,9 +212,7 @@ struct io_plan *peer_exchange_initmsg(struct io_conn *conn,
 	peer->cs = *cs;
 	peer->incoming = incoming;
 	peer->is_websocket = is_websocket;
-
-	/* Attach timer to early peer, so it gets freed with it. */
-	notleak(tal_steal(peer, timeout));
+	peer->timeout = timeout;
 
 	/* BOLT #1:
 	 *
```
