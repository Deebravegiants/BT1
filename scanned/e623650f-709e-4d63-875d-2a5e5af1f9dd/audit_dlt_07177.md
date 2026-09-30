# [?] gossipd: fix crash when processing pending node_announcements.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-06-04
Source: https://github.com/ElementsProject/lightning/commit/107fc8b9fbc9ba7ddaf7720fe8608d3c56cabd2a
Type: security-commit

## Details
gossipd: fix crash when processing pending node_announcements.

When we process pending channel updates, it can cause the node_announcement
to be moved.  Then, we process a new node_announcement and go to delete
the old one, but it's already moved!

Do the obvious thing, and refresh gossmap if necessary each time around
the loop.

```
2024-05-17T02:56:12.701Z **BROKEN** gossipd: gossip_store: get delete entry offset 554921761/585584347 (version v24.02.1-151-g6e2ab02-modded)
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: common/daemon.c:38 (send_backtrace) 0x55b4c962518b
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: common/status.c:221 (status_failed) 0x55b4c962e83e
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossip_store.c:466 (gossip_store_get_with_hdr) 0x55b4c961b6e3
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossip_store.c:491 (check_msg_type) 0x55b4c961b75d
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossip_store.c:509 (gossip_store_set_flag) 0x55b4c961b8e0
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossip_store.c:561 (gossip_store_del) 0x55b4c961bb26
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossmap_manage.c:913 (process_node_announcement) 0x55b4c961c472
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossmap_manage.c:1111 (reprocess_queued_msgs) 0x55b4c961d6a6
2024-05-17T02:56:12.701Z **BROKEN** gossipd: backtrace: gossipd/gossmap_manage.c:670 (gossmap_manage_handle_get_txout_reply) 0x55b4c961d840
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: gossipd/gossipd.c:585 (recv_req) 0x55b4c9619e6a
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: common/daemon_conn.c:35 (handle_read) 0x55b4c9625436
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: ccan/ccan/io/io.c:59 (next_plan) 0x55b4c96b8506
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: ccan/ccan/io/io.c:407 (do_plan) 0x55b4c96b898d
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: ccan/ccan/io/io.c:417 (io_ready) 0x55b4c96b8a26
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: ccan/ccan/io/poll.c:453 (io_loop) 0x55b4c96ba315
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: gossipd/gossipd.c:683 (main) 0x55b4c961a84c
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: ../csu/libc-start.c:308 (__libc_start_main) 0x7f3931a3dd09
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: (null):0 ((null)) 0x55b4c9616d39
2024-05-17T02:56:12.702Z **BROKEN** gossipd: backtrace: (null):0 ((null)) 0xffffffffffffffff
2024-05-17T02:56:12.702Z **BROKEN** gossipd: STATUS_FAIL_INTERNAL_ERROR: gossip_store: get delete entry offset 554921761/585584347
```

Reported-by: Vincenzo Palazzo
Fixes: https://github.com/ElementsProject/lightning/issues/7320
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### gossipd/gossmap_manage.c
```diff
@@ -1095,7 +1095,6 @@ static void reprocess_early_cupdates(struct gossmap_manage *gm)
 static void reprocess_queued_msgs(struct gossmap_manage *gm)
 {
 	bool pending_ann_empty, early_ann_empty;
-	struct gossmap *gossmap = gossmap_manage_get_gossmap(gm);
 
 	pending_ann_empty = map_empty(&gm->pending_ann_map);
 	early_ann_empty = map_empty(&gm->early_ann_map);
@@ -1122,6 +1121,7 @@ static void reprocess_queued_msgs(struct gossmap_manage *gm)
 
 		for (size_t i = 0; i < tal_count(pnas); i++) {
 			struct gossmap_node *node;
+			struct gossmap *gossmap = gossmap_manage_get_gossmap(gm);
 
 			node = gossmap_find_node(gossmap, &pnas[i]->node_id);
 			if (!node) {
```
