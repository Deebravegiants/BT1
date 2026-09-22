# [?] sql: fix crash for large channelmoves tables.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-04-08
Source: https://github.com/ElementsProject/lightning/commit/2ba55cc64b358659e5de682f7625817eb54a9f65
Type: security-commit

## Details
sql: fix crash for large channelmoves tables.

I've reworked this: in general we should clear the refresh bit before
calling the jsonrpc to do the update.  This allows the wait callback to
set the bit again if there's more to do, so we won't lose entries.

Now it's clear that we can remove the overzealous assert.

sql: plugins/sql.c:1749: refresh_by_created_index: Assertion `td->refresh_needs != REFRESH_UNNECESSARY' failed.
sql: FATAL SIGNAL 6 (version v26.04rc2)
0x5618e147892e send_backtrace
	common/daemon.c:38
0x5618e14789bb crashdump
	common/daemon.c:83
0x7f54d10ea04f ???
	./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
0x7f54d1138eec __pthread_kill_implementation
	./nptl/pthread_kill.c:44
0x7f54d10e9fb1 __GI_raise
	../sysdeps/posix/raise.c:26
0x7f54d10d4471 __GI_abort
	./stdlib/abort.c:79
0x7f54d10d4394 __assert_fail_base
	./assert/assert.c:94
0x7f54d10e2ec1 __GI___assert_fail
	./assert/assert.c:103
0x5618e1472725 refresh_by_created_index
	plugins/sql.c:1749
0x5618e14736af one_refresh_done
	plugins/sql.c:579
0x5618e1473932 limited_list_done
	plugins/sql.c:1738
0x5618e1477418 handle_rpc_reply
	plugins/libplugin.c:1093
0x5618e1477548 rpc_conn_read_response
	plugins/libplugin.c:1398
0x5618e147ec71 next_plan
	ccan/ccan/io/io.c:60
0x5618e147ef90 do_plan
	ccan/ccan/io/io.c:422
0x5618e147f049 io_ready
	ccan/ccan/io/io.c:439
0x5618e147ffae io_loop
	ccan/ccan/io/poll.c:470
0x5618e14786af plugin_main
	plugins/libplugin.c:2461
0x5618e1474b12 main
	plugins/sql.c:2219
0x7f54d10d5249 __libc_start_call_main
	../sysdeps/nptl/libc_start_call_main.h:58
0x7f54d10d5304 __libc_start_main_impl
	../csu/libc-start.c:360
0x5618e1470710 ???
	_start+0x20:0
0xffffffffffffffff ???
	???:0

Diagnosed-by: Lagrang3 <lagrang3@protonmail.com>
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
Changelog-None: Introduced this release.

### plugins/sql.c
```diff
@@ -1746,9 +1746,8 @@ static struct command_result *refresh_by_created_index(struct command *cmd,
 	struct sql *sql = sql_of(dbq->cmd->plugin);
 	struct out_req *req;
 
-	/* Since we're relying on watches, mark refreshing unnecessary to start */
-	assert(td->refresh_needs != REFRESH_UNNECESSARY);
-	td->refresh_needs = REFRESH_UNNECESSARY;
+	/* We no longer need refresh_created, but wait could update this meanwhile. */
+	td->refresh_needs &= ~REFRESH_CREATED;
 
 	req = jsonrpc_request_start(cmd, td->cmdname,
 				    limited_list_done, forward_error,
@@ -1782,7 +1781,6 @@ static struct command_result *updated_list_done(struct command *cmd,
 		return refresh_by_created_index(cmd, td, dbq);
 	}
 
-	td->refresh_needs = REFRESH_UNNECESSARY;
 	return one_refresh_done(cmd, dbq, false);
 }
 
@@ -1794,6 +1792,7 @@ static struct command_result *paginated_refresh(struct command *cmd,
 	 * entire thing */
 	if (td->refresh_needs & REFRESH_DELETED) {
 		plugin_log(cmd->plugin, LOG_DBG, "%s: total reload due to delete", td->name);
+		/* Since this reloads everything, covers all: updates and creates */
 		td->refresh_needs = REFRESH_UNNECESSARY;
 		return default_refresh(cmd, td, dbq);
 	}
@@ -1802,6 +1801,7 @@ static struct command_result *paginated_refresh(struct command *cmd,
 		struct out_req *req;
 		plugin_log(cmd->plugin, LOG_DBG,
 			   "%s: records updated, updating from %"PRIu64, td->name, td->last_updated_index + 1);
+		td->refresh_needs &= ~REFRESH_UPDATED;
 		req = jsonrpc_request_start(cmd, td->cmdname,
 					    updated_list_done, forward_error,
 					    dbq);
```

### tests/test_plugin.py
```diff
@@ -4410,7 +4410,6 @@ def test_sql_deprecated(node_factory, bitcoind):
     assert ret == {'rows': [[1]]}
 
 
-@pytest.mark.xfail(strict=True)
 def test_sql_limit_per_list(node_factory):
     l1, l2, l3 = node_factory.line_graph(
         3, wait_for_announce=True, opts=[{}, {"dev-sqllistlimit": 10}, {}]
```
