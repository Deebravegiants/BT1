# [?] plugins/sql: fix crash when subobject is missing which has subobject inside it.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-08-15
Source: https://github.com/ElementsProject/lightning/commit/054eeb8aa21fa1bd01b77d3271cccf0cdb66e973
Type: security-commit

## Details
plugins/sql: fix crash when subobject is missing which has subobject inside it.

There's only one place (added in v24.02) where we have nested subobjects, and
if the outer sub-object is not there it crashes.

```
sql: FATAL SIGNAL 11 (version v24.08rc1-2-ge134f2f-modded)
0x5781d447239b send_backtrace
        common/daemon.c:33
0x5781d4472432 crashdump
        common/daemon.c:75
0x787bcd64531f ???
        ./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
0x5781d447782a json_get_membern
        common/json_parse_simple.c:210
0x5781d44778cc json_get_member
        common/json_parse_simple.c:223
0x5781d445d0e2 process_json_obj
        plugins/sql.c:537
0x5781d445d10d process_json_obj
        plugins/sql.c:538
0x5781d445d598 process_json_list
        plugins/sql.c:684
0x5781d445d65a process_json_result
        plugins/sql.c:699
0x5781d445d7cb default_list_done
        plugins/sql.c:722
0x5781d446349d handle_rpc_reply
        plugins/libplugin.c:1016
0x5781d4463640 rpc_read_response_one
        plugins/libplugin.c:1202
0x5781d44636f1 rpc_conn_read_response
        plugins/libplugin.c:1226
0x5781d459e56c next_plan
        ccan/ccan/io/io.c:60
0x5781d459ea3d do_plan
        ccan/ccan/io/io.c:422
0x5781d459eafa io_ready
        ccan/ccan/io/io.c:439
0x5781d45a0469 io_loop
        ccan/ccan/io/poll.c:455
0x5781d4463dcb plugin_main
        plugins/libplugin.c:2230
```

Changelog-Fixed: Plugins: `sql` crash on querying `listpeerchannels` during channel establishment.
Fixes: https://github.com/ElementsProject/lightning/issues/7505
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/sql.c
```diff
@@ -534,7 +534,11 @@ static struct command_result *process_json_obj(struct command *cmd,
 			if (!col->sub->is_subobject)
 				continue;
 
-			coltok = json_get_member(buf, t, col->jsonname);
+			/* This can happen if the field is missing */
+			if (!t)
+				coltok = NULL;
+			else
+				coltok = json_get_member(buf, t, col->jsonname);
 			ret = process_json_obj(cmd, buf, coltok, col->sub, row, this_rowid,
 					       NULL, sqloff, stmt);
 			if (ret)
```

### tests/test_plugin.py
```diff
@@ -4395,3 +4395,23 @@ def test_autoclean_batch(node_factory):
     l1.rpc.setconfig('autoclean-cycle', 5)
     wait_for(lambda: l1.rpc.autoclean_status('expiredinvoices')
              == {'autoclean': {'expiredinvoices': {'enabled': True, 'cleaned': 200, 'age': 2}}})
+
+
+def test_sql_crash(node_factory, bitcoind):
+    """sub-object with inner-sub-object is missing -> Crash.  This only
+    happens for local and remote inside listpeerchannels.update (for
+    now).
+
+    """
+    l1, l2 = node_factory.line_graph(2, fundchannel=False)
+
+    addr = l1.rpc.newaddr()['bech32']
+    bitcoind.rpc.sendtoaddress(addr, 1)
+    bitcoind.generate_block(1)
+
+    wait_for(lambda: l1.rpc.listfunds()['outputs'] != [])
+
+    l1.rpc.fundchannel_start(l2.info['id'], '10000000sat')
+
+    assert 'updates' not in only_one(l1.rpc.listpeerchannels()['channels'])
+    l1.rpc.sql(f"SELECT * FROM peerchannels;")
```
