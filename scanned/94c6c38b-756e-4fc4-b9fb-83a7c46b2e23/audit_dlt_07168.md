# [?] common: fix crash when we have a localmod with unrepresentable fee values.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-03-31
Source: https://github.com/ElementsProject/lightning/commit/8dae8be5fb0991bb08e78ae0e3cf78157945ca99
Type: security-commit

## Details
common: fix crash when we have a localmod with unrepresentable fee values.

We handed NULL as the logcb, resulting in a very uninformative crash:

```
2025-03-14T03:46:36.447Z INFO    lightningd: Server started with public key 03d67f36c4f81789e2fe425028bacc96b199813eae426c517f589a45f1136c1fe5, alias Jubilee (color #dc42f4) and lightningd v25.02
topology: FATAL SIGNAL 11 (version v25.02)
0x560037f64aad send_backtrace
        common/daemon.c:33
0x560037f64b49 crashdump
        common/daemon.c:78
0x7f6c41ff351f ???
        ./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
0x0 ???
        ???:0
```

Changelog-Fixed: `topology` crash on invoice creation if a peer had a really high feerate.
Fixes: https://github.com/ElementsProject/lightning/issues/8156
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### common/gossmap.c
```diff
@@ -551,10 +551,11 @@ static void fill_from_update(struct gossmap *map,
 	    || hc->delay != delay) {
 		hc->htlc_max = 0;
 		hc->enabled = false;
-		logcb(cbarg, LOG_DBG,
-		      "Bad cupdate for %s, ignoring (delta=%u, fee=%u/%u)",
-		      fmt_short_channel_id_dir(tmpctx, scidd),
-		      delay, base_fee, proportional_fee);
+		if (logcb)
+			logcb(cbarg, LOG_DBG,
+			      "Bad cupdate for %s, ignoring (delta=%u, fee=%u/%u)",
+			      fmt_short_channel_id_dir(tmpctx, scidd),
+			      delay, base_fee, proportional_fee);
 	}
 }
 
```

### tests/test_gossip.py
```diff
@@ -2358,3 +2358,16 @@ def test_gossip_seeker_autoconnect(node_factory):
                            rf'{l3.info["id"]} for additional gossip')
     l1.daemon.wait_for_log('gossipd: seeker: starting gossip')
     assert l3.info['id'] in [n['id'] for n in l1.rpc.listpeers()['peers']]
+
+
+def test_incoming_unreasonable(node_factory):
+    """Don't crash if we have a local incoming channel with unreasonable (i.e. internally-unrepresentable) fees"""
+    l1, l2, l3, l4 = node_factory.line_graph(4,
+                                             wait_for_announce=True,
+                                             opts={'allow_bad_gossip': True})
+
+    l2.rpc.setchannel(l3.info['id'], 100000000)
+    l4.rpc.setchannel(l3.info['id'], 100000000)
+    wait_for(lambda: [c['updates']['remote']['fee_base_msat'] for c in l3.rpc.listpeerchannels()['channels']] == [100000000, 100000000])
+    l3.restart()
+    l3.rpc.listincoming()
```
