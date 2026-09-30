# [?] connectd: fix crash when we get an incoming conn while outgoing attempt is ratelimited.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-11-28
Source: https://github.com/ElementsProject/lightning/commit/2e90f59dfea760fd0c39abeb1d333c5d85c2a1c2
Type: security-commit

## Details
connectd: fix crash when we get an incoming conn while outgoing attempt is ratelimited.

```
Program received signal SIGSEGV, Segmentation fault.
0x000000001014e9d8 in io_set_finish_ (conn=0x0, finish=0x0, arg=0x0) at ccan/ccan/io/io.c:137
137             conn->finish = finish;
(gdb) bt
    incoming=true) at connectd/connectd.c:394
```

Fixes: #7871
Reported-by: grubles
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
Changelog-None: broken in this release

## Patch
### connectd/connectd.c
```diff
@@ -390,8 +390,10 @@ struct io_plan *peer_connected(struct io_conn *conn,
 
 	if (connect) {
 		/*~ Now we've connected, disable the callback which would
-		 * cause us to to try the next address on failure. */
-		io_set_finish(connect->conn, NULL, NULL);
+		 * cause us to to try the next address on failure (if it's
+		 * in progress right now) */
+		if (connect->conn)
+			io_set_finish(connect->conn, NULL, NULL);
 		tal_free(connect);
 	}
 
```
