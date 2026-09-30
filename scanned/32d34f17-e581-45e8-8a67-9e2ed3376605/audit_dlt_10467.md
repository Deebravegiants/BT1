# [?] connectd: rescue constant message size feature by exploiting OPT_ONION_MESSAGES (LND)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-04-08
Source: https://github.com/ElementsProject/lightning/commit/52b70043ab2652768238ca2ff3e93b185c6ed6c3
Type: security-commit

## Details
connectd: rescue constant message size feature by exploiting OPT_ONION_MESSAGES (LND)

I 🧡 Laolu!

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### connectd/multiplex.c
```diff
@@ -481,9 +481,13 @@ static bool have_empty_encrypted_queue(const struct peer *peer)
 	return membuf_num_elems(&peer->encrypted_peer_out) == 0;
 }
 
+/* Funny story: we discovered an LND bug, where they hung up if we sent
+ * "no reply" ping messages.  This was fixed in (the upcoming) v21, which
+ * Laolu pointed out also supports onion messages.  Hence we use that
+ * to detect if we should pad packets. */
 static bool use_uniform_writes(const struct peer *peer)
 {
-	return peer->daemon->dev_uniform_padding;
+	return feature_offered(peer->their_features, OPT_ONION_MESSAGES);
 }
 
 /* (Continue) writing the encrypted_peer_out array */
```
