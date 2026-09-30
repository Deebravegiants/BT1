# [?] autoclean: fix timer crash when we're cleaning two things at once.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-02-26
Source: https://github.com/ElementsProject/lightning/commit/38d90b250596d38a777ab064c3788a730f14d753
Type: security-commit

## Details
autoclean: fix timer crash when we're cleaning two things at once.

If we had two things to clean, we fired off two requests (eg.
listforwards and listinvoices) and both marked the timer as finished,
triggering an assert.

We already have a refcount for outstanding requests to avoid this
for e.g. outstanding del commands, so use it here too!

```
Jan 19 19:20:00  lightningd[748044]: autoclean: plugins/libplugin.c:445: timer_complete: Assertion `p->in_timer > 0' failed.
Jan 19 19:20:00  lightningd[748044]: autoclean: FATAL SIGNAL 6 (version v22.11.1)
Jan 19 19:20:00  lightningd[748044]: 0x562c388136e4 send_backtrace
Jan 19 19:20:00  lightningd[748044]:         common/daemon.c:33
Jan 19 19:20:00  lightningd[748044]: 0x562c3881376c crashdump
Jan 19 19:20:00  lightningd[748044]:         common/daemon.c:46
Jan 19 19:20:00  lightningd[748044]: 0x7f26d0898d5f ???
Jan 19 19:20:00  lightningd[748044]:         ./signal/../sysdeps/unix/sysv/linux/x86_64/sigaction.c:0
Jan 19 19:20:00  lightningd[748044]: 0x7f26d0898ce1 __GI_raise
Jan 19 19:20:00  lightningd[748044]:         ../sysdeps/unix/sysv/linux/raise.c:51
Jan 19 19:20:00  lightningd[748044]: 0x7f26d0882536 __GI_abort
Jan 19 19:20:00  lightningd[748044]:         ./stdlib/abort.c:79
Jan 19 19:20:00  lightningd[748044]: 0x7f26d088240e __assert_fail_base
Jan 19 19:20:00  lightningd[748044]:         ./assert/assert.c:92
Jan 19 19:20:00  lightningd[748044]: 0x7f26d0891661 __GI___assert_fail
Jan 19 19:20:00  lightningd[748044]:         ./assert/assert.c:101
Jan 19 19:20:00  lightningd[748044]: 0x562c3880355d timer_complete
Jan 19 19:20:00  lightningd[748044]:         plugins/libplugin.c:445
Jan 19 19:20:00  lightningd[748044]: 0x562c38800b54 clean_finished
Jan 19 19:20:00  lightningd[748044]:         plugins/autoclean.c:122
Jan 19 19:20:00  lightningd[748044]: 0x562c388010ed clean_finished_one
Jan 19 19:20:00  lightningd[748044]:         plugins/autoclean.c:132
Jan 19 19:20:00  lightningd[748044]: 0x562c388011b6 del_done
Jan 19 19:20:00  lightningd[748044]:         plugins/autoclean.c:149
Jan 19 19:20:00  lightningd[748044]: 0x562c388058b5 handle_rpc_reply
Jan 19 19:20:00  lightningd[748044]:         plugins/libplugin.c:768
Jan 19 19:20:00  lightningd[748044]: 0x562c38805a39 rpc_read_response_one
Jan 19 19:20:00  lightningd[748044]:         plugins/libplugin.c:944
Jan 19 19:20:00  lightningd[748044]: 0x562c38805ad7 rpc_conn_read_response
Jan 19 19:20:00  lightningd[748044]:         plugins/libplugin.c:968
Jan 19 19:20:00  lightningd[748044]: 0x562c38876b60 next_plan
Jan 19 19:20:00  lightningd[748044]:         ccan/ccan/io/io.c:59
Jan 19 19:20:00  lightningd[748044]: 0x562c38876fe7 do_plan
Jan 19 19:20:00  lightningd[748044]:         ccan/ccan/io/io.c:407
Jan 19 19:20:00  lightningd[748044]: 0x562c38877080 io_ready
Jan 19 19:20:00  lightningd[748044]:         ccan/ccan/io/io.c:417
Jan 19 19:20:00  lightningd[748044]: 0x562c3887823c io_loop
Jan 19 19:20:00  lightningd[748044]:         ccan/ccan/io/poll.c:453
Jan 19 19:20:00  lightningd[748044]: 0x562c38805d11 plugin_main
Jan 19 19:20:00  lightningd[748044]:         plugins/libplugin.c:1801
Jan 19 19:20:00  lightningd[748044]: 0x562c38801c7a main
Jan 19 19:20:00  lightningd[748044]:         plugins/autoclean.c:613
```

Fixes: #5912
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/autoclean.c
```diff
@@ -227,9 +227,7 @@ static struct command_result *listinvoices_done(struct command *cmd,
 			cinfo->num_uncleaned++;
 	}
 
-	if (cinfo->cleanup_reqs_remaining)
-		return command_still_pending(cmd);
-	return clean_finished(cinfo);
+	return clean_finished_one(cinfo);
 }
 
 static struct command_result *listsendpays_done(struct command *cmd,
@@ -289,9 +287,7 @@ static struct command_result *listsendpays_done(struct command *cmd,
 		}
 	}
 
- 	if (cinfo->cleanup_reqs_remaining)
-		return command_still_pending(cmd);
-	return clean_finished(cinfo);
+	return clean_finished_one(cinfo);
 }
 
 static struct command_result *listforwards_done(struct command *cmd,
@@ -368,9 +364,7 @@ static struct command_result *listforwards_done(struct command *cmd,
 		}
 	}
 
- 	if (cinfo->cleanup_reqs_remaining)
-		return command_still_pending(cmd);
-	return clean_finished(cinfo);
+	return clean_finished_one(cinfo);
 }
 
 static struct command_result *listsendpays_failed(struct command *cmd,
@@ -399,7 +393,7 @@ static struct command_result *listforwards_failed(struct command *cmd,
 
 static struct command_result *do_clean(struct clean_info *cinfo)
 {
-	struct out_req *req = NULL;
+	struct out_req *req;
 
 	cinfo->cleanup_reqs_remaining = 0;
 	cinfo->num_uncleaned = 0;
@@ -411,6 +405,7 @@ static struct command_result *do_clean(struct clean_info *cinfo)
 					    listsendpays_done, listsendpays_failed,
 					    cinfo);
 		send_outreq(plugin, req);
+		cinfo->cleanup_reqs_remaining++;
 	}
 
 	if (cinfo->subsystem_age[EXPIREDINVOICES] != 0
@@ -419,6 +414,7 @@ static struct command_result *do_clean(struct clean_info *cinfo)
 					    listinvoices_done, listinvoices_failed,
 					    cinfo);
 		send_outreq(plugin, req);
+		cinfo->cleanup_reqs_remaining++;
 	}
 
 	if (cinfo->subsystem_age[SUCCEEDEDFORWARDS] != 0
@@ -427,12 +423,12 @@ static struct command_result *do_clean(struct clean_info *cinfo)
 					    listforwards_done, listforwards_failed,
 					    cinfo);
 		send_outreq(plugin, req);
+		cinfo->cleanup_reqs_remaining++;
 	}
 
-	if (req)
+	if (cinfo->cleanup_reqs_remaining)
 		return command_still_pending(NULL);
-	else
-		return clean_finished(cinfo);
+	return clean_finished(cinfo);
 }
 
 /* Needs a different signature than do_clean */
```

### tests/test_plugin.py
```diff
@@ -3142,6 +3142,14 @@ def test_autoclean(node_factory):
     assert l2.rpc.getinfo()['fees_collected_msat'] == amt_before
 
 
+def test_autoclean_timer_crash(node_factory):
+    """Running two autocleans at once crashed timer code"""
+    node_factory.get_node(options={'autoclean-cycle': 1,
+                                   'autoclean-failedforwards-age': 31536000,
+                                   'autoclean-expiredinvoices-age': 31536000})
+    time.sleep(20)
+
+
 def test_autoclean_once(node_factory):
     l1, l2, l3 = node_factory.line_graph(3, opts={'may_reconnect': True},
                                          wait_for_announce=True)
```
