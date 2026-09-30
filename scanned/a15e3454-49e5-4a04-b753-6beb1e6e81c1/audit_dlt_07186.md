# [?] lightningd: fix crash on shutdown while if channel being cancelled at same time.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-06-22
Source: https://github.com/ElementsProject/lightning/commit/ffb0f03e1a0945f651d36cfbd27d2423ce4fd7d1
Type: security-commit

## Details
lightningd: fix crash on shutdown while if channel being cancelled at same time.

```
 DEBUG   lightningd: Command returned result after jcon close
 DEBUG   connectd: Shutting down
 DEBUG   gossipd: Shutting down
 DEBUG   hsmd: Shutting down
 **BROKEN** lightningd: FATAL SIGNAL 6 (version b29955a-modded)
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/common/daemon.c:38 (send_backtrace) 0x55fea4a13a08
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/common/daemon.c:75 (crashdump) 0x55fea4a140a1
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f9ea680651f
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f9ea685aa7c
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f9ea6806475
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f9ea67ec7f2
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:95 (call_error) 0x55fea4bbef68
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:169 (check_bounds) 0x55fea4bbfa68
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:180 (to_tal_hdr) 0x55fea4bbdefe
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:193 (to_tal_hdr_or_null) 0x55fea4bbd9cf
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:461 (tal_alloc_) 0x55fea4bbd893
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:506 (tal_alloc_arr_) 0x55fea4bbdce6
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/str/str.c:91 (tal_vfmt_) 0x55fea4bbc95e
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/lightningd/jsonrpc.c:502 (command_fail) 0x55fea499c427
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/lightningd/channel.c:81 (destroy_channel) 0x55fea4976a31
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:246 (notify) 0x55fea4bbdc18
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:437 (del_tree) 0x55fea4bbe028
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/ccan/ccan/tal/tal.c:521 (tal_free) 0x55fea4bbde84
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/lightningd/lightningd.c:577 (free_all_channels) 0x55fea49a2660
 **BROKEN** lightningd: backtrace: /home/runner/work/lightning/lightning/lightningd/lightningd.c:1280 (main) 0x55fea49a1530
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f9ea67edd8f
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f9ea67ede3f
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x55fea496ef04
 **BROKEN** lightningd: backtrace: (null):0 ((null)) 0xffffffffffffffff
```

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/channel_control.c
```diff
@@ -1079,6 +1079,10 @@ struct command_result *cancel_channel_before_broadcast(struct command *cmd,
 	}
 
 	tal_arr_expand(&cancel_channel->forgets, cmd);
+	/* Now, cmd will be ended by forget() or process_check_funding_broadcast(),
+	 * but in the shutdown case it might be freed first and those crash.  So instead
+	 * we make it a child if forgets so it will stay around at least that long! */
+	tal_steal(cancel_channel->forgets, cmd);
 
 	/* Check if the transaction is onchain. */
 	/* Note: The above check and this check can't completely ensure that
```
