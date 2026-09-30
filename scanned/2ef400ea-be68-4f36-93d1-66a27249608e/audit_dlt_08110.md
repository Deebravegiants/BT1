# [?] sql: fix crash on fresh node_announcment.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-02-27
Source: https://github.com/ElementsProject/lightning/commit/f3baa3e510b6e1e27e34e835df4df16d9b62ca98
Type: security-commit

## Details
sql: fix crash on fresh node_announcment.

Missing quotes when we delete the old one!

Reported-by: Alex Myers
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/sql.c
```diff
@@ -850,7 +850,7 @@ static void delete_node_from_db(struct command *cmd,
 	err = sqlite3_exec(db,
 			   tal_fmt(tmpctx,
 				   "DELETE FROM nodes"
-				   " WHERE nodeid = %s",
+				   " WHERE nodeid = '%s'",
 				   node_id_to_hexstr(tmpctx, id)),
 			   NULL, NULL, &errmsg);
 	if (err != SQLITE_OK)
```

### tests/test_plugin.py
```diff
@@ -3288,12 +3288,14 @@ def test_block_added_notifications(node_factory, bitcoind):
 @pytest.mark.developer("wants dev-announce-localhost so we see listnodes.addresses")
 def test_sql(node_factory, bitcoind):
     opts = {'experimental-offers': None,
-            'dev-allow-localhost': None}
+            'dev-allow-localhost': None,
+            'may_reconnect': True}
     l2opts = {'lease-fee-basis': 50,
               'lease-fee-base-sat': '2000msat',
               'channel-fee-max-base-msat': '500sat',
               'channel-fee-max-proportional-thousandths': 200,
-              'sqlfilename': 'sql.sqlite3'}
+              'sqlfilename': 'sql.sqlite3',
+              'may_reconnect': True}
     l2opts.update(opts)
     l1, l2, l3 = node_factory.line_graph(3, wait_for_announce=True,
                                          opts=[opts, l2opts, opts])
@@ -3920,6 +3922,18 @@ def test_sql(node_factory, bitcoind):
                       " option_will_fund_compact_lease"
                       " FROM nodes WHERE HEX(nodeid) = '{}';".format(l1.info['id'].upper())) == {'rows': [[None] * 6]}
 
+    # Test that nodes get updated.
+    l2.stop()
+    l2.daemon.opts["alias"] = "TESTALIAS"
+    # Don't try to reuse the same db file!
+    del l2.daemon.opts["sqlfilename"]
+    l2.start()
+    # DEV appends stuff to alias!
+    alias = l2.rpc.getinfo()['alias']
+    assert alias == "TESTALIAS"
+    l2.rpc.connect(l3.info['id'], 'localhost', l3.port)
+    wait_for(lambda: l3.rpc.sql("SELECT * FROM nodes WHERE alias = '{}'".format(alias))['rows'] != [])
+
 
 def test_sql_deprecated(node_factory, bitcoind):
     # deprecated-apis breaks schemas...
```
