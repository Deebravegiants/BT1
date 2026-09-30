# [?] http: fix Sec-WebSocket-Key decode stack overflow (#10142)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-09
Source: https://github.com/firedancer-io/firedancer/commit/a4795c54fd0794cb4ae6274b1bbf111246f243b1
Type: security-commit

## Details
http: fix Sec-WebSocket-Key decode stack overflow (#10142)

decoded_key was sized 16 bytes, but fd_base64_decode writes up to
FD_BASE64_DEC_SZ(24)==18 bytes before returning the length we check.
An unpadded 24 char key decodes to 18 bytes, overflowing the stack
by 2 attacker-controlled bytes.  Size the buffer to the decoder's
max output and make test_ws_bad_key_close actually reach the decode.

## Patch
### src/waltz/http/fd_http_server.c
```diff
@@ -609,7 +609,7 @@ read_conn_http( fd_http_server_t * http,
         /* RFC 6455 s4.2.1: Sec-WebSocket-Key must base64-decode to
            exactly 16 bytes.  fd_base64_decode also validates the
            alphabet and padding rules. */
-        uchar decoded_key[ 16 ];
+        uchar decoded_key[ FD_BASE64_DEC_SZ( 24UL ) ];
         if( FD_UNLIKELY( 16L!=fd_base64_decode( decoded_key, sec_websocket_key, 24UL ) ) ) {
           close_conn( http, conn_idx, FD_HTTP_SERVER_CONNECTION_CLOSE_WS_BAD_KEY );
           return;
```

### src/waltz/http/test_http_server.c
```diff
@@ -304,14 +304,14 @@ test_duplicate_content_length_different_close( void ) {
 void
 test_ws_bad_key_close( void ) {
   FD_LOG_NOTICE(( "Testing WebSocket bad Sec-WebSocket-Key" ));
-  /* Key is 24 chars but has invalid base64 (padding in wrong
-     place), so fd_base64_decode returns != 16. */
+  /* Key is 24 chars but unpadded, so it decodes to 18 bytes and
+     fd_base64_decode returns != 16 (regression test for decoded_key). */
   test_close_reason(
       "GET / HTTP/1.1\r\n"
       "Host: localhost\r\n"
       "Upgrade: websocket\r\n"
       "Connection: Upgrade\r\n"
-      "Sec-WebSocket-Key: ====aGVsbG8gd29ybGQ=\r\n"
+      "Sec-WebSocket-Key: AAAAAAAAAAAAAAAAAAAAAAAA\r\n"
       "Sec-WebSocket-Version: 13\r\n"
       "\r\n",
       FD_HTTP_SERVER_CONNECTION_CLOSE_WS_BAD_KEY,
```
