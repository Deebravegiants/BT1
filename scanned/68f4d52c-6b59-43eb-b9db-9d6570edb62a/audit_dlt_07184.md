# [?] lightningd: fix crash caused by sending channeld message to closingd

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-10-16
Source: https://github.com/ElementsProject/lightning/commit/91699d8483e7fed7794e020978bba3f2baaaf57c
Type: security-commit

## Details
lightningd: fix crash caused by sending channeld message to closingd

```
Sending closingd an invalid message 03f40000006d
...
0x564b55bb7378 fatal
	lightningd/log.c:1035
0x564b55bf7841 subd_send_msg
	lightningd/subd.c:841
0x564b55b87d08 try_update_blockheight
	lightningd/channel_control.c:143
0x564b55b8c497 channel_notify_new_block
	lightningd/channel_control.c:1687
0x564b55bb26bb notify_new_block
	lightningd/lightningd.c:743
```

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/channel_control.c
```diff
@@ -130,7 +130,7 @@ static void try_update_blockheight(struct lightningd *ld,
 	}
 
 	/* If we're not opened/locked in yet, don't send update */
-	if (!channel_state_fees_can_change(channel->state))
+	if (!channel_state_can_add_htlc(channel->state))
 		return;
 
 	/* We don't update the blockheight for non-leased chans */
```
