# [?] http_server: fix NULL terminator oob (#9094)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-31
Source: https://github.com/firedancer-io/firedancer/commit/fa96bdbcb2471412e604fd5ec4a4e5b62bdf358f
Type: security-commit

## Details
http_server: fix NULL terminator oob (#9094)

## Patch
### src/waltz/http/fd_http_server.c
```diff
@@ -1419,7 +1419,8 @@ fd_http_server_printf( fd_http_server_t * http,
   ulong printed_len = (ulong)vsnprintf( NULL, 0UL, fmt, ap );
   va_end( ap );
 
-  fd_http_server_reserve( http, printed_len );
+  /* reserve enough for the NULL terminator */
+  fd_http_server_reserve( http, printed_len+1UL );
   if( FD_UNLIKELY( http->stage_err ) ) return;
 
   va_start( ap, fmt );
```

### src/waltz/http/test_http_server.c
```diff
@@ -86,7 +86,7 @@ test_oring( void ) {
       for( ulong k=0UL; k<i; k++ ) fd_http_server_printf( http, "%c", (char)('a'+i) );
 
       fd_http_server_response_t response;
-      if( i>8 ) {
+      if( i>7 ) {
         FD_TEST( fd_http_server_stage_body( http, &response ) );
       } else {
         FD_TEST( !fd_http_server_stage_body( http, &response ) );
@@ -102,23 +102,23 @@ test_oring( void ) {
   fd_http_server_response_t response;
 
   http->stage_off = 1UL;
-  fd_http_server_printf( http, "01234567" );
+  fd_http_server_printf( http, "0123456" );
   FD_TEST( http->stage_off==8UL );
-  FD_TEST( http->stage_len==8UL );
+  FD_TEST( http->stage_len==7UL );
   FD_TEST( !fd_http_server_stage_body( http, &response ) );
   FD_TEST( http->stage_comp_len==0UL );
 
   http->stage_off = 7UL;
-  fd_http_server_printf( http, "01234567" );
+  fd_http_server_printf( http, "0123456" );
   FD_TEST( http->stage_off==8UL );
-  FD_TEST( http->stage_len==8UL );
+  FD_TEST( http->stage_len==7UL );
   fd_http_server_unstage( http );
   FD_TEST( http->stage_comp_len==0UL );
 
   http->stage_off = 16UL;
-  fd_http_server_printf( http, "01234567" );
+  fd_http_server_printf( http, "0123456" );
   FD_TEST( http->stage_off==16UL );
-  FD_TEST( http->stage_len==8UL );
+  FD_TEST( http->stage_len==7UL );
   FD_TEST( !fd_http_server_stage_body( http, &response ) );
   FD_TEST( http->stage_comp_len==0UL );
 
```
