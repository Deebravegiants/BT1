# [?] connectd: rescue constant message size feature by exploiting option 154 (Eclair).

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-04-08
Source: https://github.com/ElementsProject/lightning/commit/a65c6975554bf90a9f835ab16783127451a46e66
Type: security-commit

## Details
connectd: rescue constant message size feature by exploiting option 154 (Eclair).

I 🧡 tbast!

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### connectd/multiplex.c
```diff
@@ -485,9 +485,16 @@ static bool have_empty_encrypted_queue(const struct peer *peer)
  * "no reply" ping messages.  This was fixed in (the upcoming) v21, which
  * Laolu pointed out also supports onion messages.  Hence we use that
  * to detect if we should pad packets. */
+
+/* Funnier story: Eclair had the same bug, and have also committed a
+ * fix.  They currently use a boutique feature bit 154, which is
+ * "Phoenix-specific custom splices implementation" which Tbast
+ * indicates is being phased out.  So if they offer that, don't send
+ * such pings. */
 static bool use_uniform_writes(const struct peer *peer)
 {
-	return feature_offered(peer->their_features, OPT_ONION_MESSAGES);
+	return feature_offered(peer->their_features, OPT_ONION_MESSAGES)
+		&& !feature_offered(peer->their_features, 154);
 }
 
 /* (Continue) writing the encrypted_peer_out array */
```
