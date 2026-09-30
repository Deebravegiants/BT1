# [?] lightningd: fix crash in "shouldn't happen" path.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-05-16
Source: https://github.com/ElementsProject/lightning/commit/40a86daaf5b8cab2dda6408d05175033a4f4874c
Type: security-commit

## Details
lightningd: fix crash in "shouldn't happen" path.

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/channel_gossip.c
```diff
@@ -1096,12 +1096,12 @@ void channel_gossip_update_from_gossipd(struct channel *channel,
 	case CGOSSIP_CHANNEL_ANNOUNCED_DYING:
 	case CGOSSIP_CHANNEL_ANNOUNCED_DEAD:
 		/* Shouldn't happen. */
-		if (taken(channel_update))
-			tal_free(channel_update);
 		log_broken(channel->log,
 			   "gossipd gave channel_update in %s? update=%s",
 			   channel_gossip_state_str(channel->channel_gossip->state),
 			   tal_hex(tmpctx, channel_update));
+		if (taken(channel_update))
+			tal_free(channel_update);
 		return;
 
 	/* This happens: we step back a block when restarting. */
```
