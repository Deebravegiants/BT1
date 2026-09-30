# [?] connectd: fix crash on freed context for new connections.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-03-06
Source: https://github.com/ElementsProject/lightning/commit/b5c614069bec50ae0e084ad8ac24c17a8729b619
Type: security-commit

## Details
connectd: fix crash on freed context for new connections.

ccan/io stores the context pointer for io_new_conn, but we were using
`daemon->listeners` which we reallocate, so it can use a stale pointer.

```
0x3e1700 call_error
	ccan/ccan/tal/tal.c:93
0x3e1700 check_bounds
	ccan/ccan/tal/tal.c:165
0x3e1700 to_tal_hdr
	ccan/ccan/tal/tal.c:174
0x3e1211 to_tal_hdr_or_null
	ccan/ccan/tal/tal.c:186
0x3e1211 tal_alloc_
	ccan/ccan/tal/tal.c:426
0x3db8f4 io_new_conn_
	ccan/ccan/io/io.c:91
0x3dd2e1 accept_conn
	ccan/ccan/io/poll.c:277
0x3dd2e1 io_loop
	ccan/ccan/io/poll.c:444
0x3419fa main
	connectd/connectd.c:2081
```

Fixes: #6060
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### connectd/connectd.c
```diff
@@ -1570,7 +1570,7 @@ static void connect_activate(struct daemon *daemon, const u8 *msg)
 			}
 			/* Add to listeners array */
 			tal_arr_expand(&daemon->listeners,
-				       io_new_listener(daemon->listeners,
+				       io_new_listener(daemon,
 						       daemon->listen_fds[i]->fd,
 						       get_in_cb(daemon->listen_fds[i]
 								 ->is_websocket),
```
