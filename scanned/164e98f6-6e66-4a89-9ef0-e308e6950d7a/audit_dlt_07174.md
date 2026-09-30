# [?] channeld: fix crash with pre-TLV peers.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-09-07
Source: https://github.com/ElementsProject/lightning/commit/78b9ccf4322078c2a1e7772f86ef30861d5cf74d
Type: security-commit

## Details
channeld: fix crash with pre-TLV peers.

send_tlvs is NULL if no special features are supported, and peer
sets `next_to_send` anyway:

```
0x5ed1c6719538 peer_reconnect
channeld/channeld.c:5205
0x5ed1c6719dab init_channel
channeld/channeld.c:5959
0x5ed1c6719f04 main
channeld/channeld.c:6005
```

Backport: v24.08
Fixes: https://github.com/ElementsProject/lightning/issues/7486
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### channeld/channeld.c
```diff
@@ -5158,7 +5158,7 @@ static void peer_reconnect(struct peer *peer,
 	} else if (pending_updates(peer->channel, LOCAL, true)
 		   || pending_updates(peer->channel, REMOTE, true)) {
 		status_debug("No upgrade: pending changes");
-	} else {
+	} else if (send_tlvs && recv_tlvs) {
 		const struct tlv_channel_reestablish_tlvs *initr, *ninitr;
 		const u8 *type;
 
```
