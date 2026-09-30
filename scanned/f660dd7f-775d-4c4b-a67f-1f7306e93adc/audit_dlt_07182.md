# [?] lightnignd: Fix another assert crash.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-02-15
Source: https://github.com/ElementsProject/lightning/commit/23460eb89d2e193a5ad2425029c1da7c5275feac
Type: security-commit

## Details
lightnignd: Fix another assert crash.

If we accept a channel_update in state "NEED_SIGS" we should not set
refresh timer: we're simply holding it for the moment we get to that state
(which will happen as we mine the block).

```
0x7fd1cce39205 __assert_fail
	./assert/assert.c:101
0x55c103cc6ee9 check_channel_gossip
	lightningd/channel_gossip.c:128
0x55c103cc8a13 channel_gossip_update_from_gossipd
	lightningd/channel_gossip.c:821
0x55c103cd752d handle_init_cupdate
	lightningd/gossip_control.c:138
0x55c103cd79a3 gossip_msg
	lightningd/gossip_control.c:190
```

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/channel_gossip.c
```diff
@@ -140,7 +140,8 @@ static void check_channel_gossip(const struct channel *channel)
 static void cupdate_timer_refresh(struct channel *channel);
 
 static void set_public_cupdate(struct channel *channel,
-			       const u8 *cupdate TAKES)
+			       const u8 *cupdate TAKES,
+			       bool refresh_later)
 {
 	struct lightningd *ld = channel->peer->ld;
 	struct channel_gossip *cg = channel->channel_gossip;
@@ -162,7 +163,7 @@ static void set_public_cupdate(struct channel *channel,
 	cg->refresh_timer = tal_free(cg->refresh_timer);
 
 	/* If enabled, we refresh, based on old timestamp */
-	if (!enabled)
+	if (!enabled || !refresh_later)
 		return;
 
 	due.ts.tv_sec = timestamp;
@@ -338,7 +339,8 @@ static void broadcast_public_cupdate(struct channel *channel,
 		return;
 
 	set_public_cupdate(channel,
-			   take(sign_update(NULL, channel->peer->ld, cupdate)));
+			   take(sign_update(NULL, channel->peer->ld, cupdate)),
+			   true);
 
 	subd_req(ld->gossip, ld->gossip,
 		 take(towire_gossipd_addgossip(NULL, cg->cupdate, NULL)),
@@ -817,7 +819,10 @@ void channel_gossip_update_from_gossipd(struct channel *channel,
 		break;
 	}
 
-	set_public_cupdate(channel, channel_update);
+	/* We don't set refresh timer if we're not ANNOUNCED, we're just saving updates
+	 * for later! */
+	set_public_cupdate(channel, channel_update,
+			   channel->channel_gossip->state == CGOSSIP_ANNOUNCED);
 	check_channel_gossip(channel);
 }
 
```
