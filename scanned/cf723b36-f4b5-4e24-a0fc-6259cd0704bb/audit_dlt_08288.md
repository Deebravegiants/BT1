# [?] h2: fix off-by-one oob in matcher

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-06-04
Source: https://github.com/firedancer-io/firedancer/commit/8289abfcf2b3e9de31f1cb0d0797c2e2e41b8df9
Type: security-commit

## Details
h2: fix off-by-one oob in matcher

## Patch
### src/waltz/h2/fd_h2_hdr_match.c
```diff
@@ -50,7 +50,7 @@ fd_h2_hdr_matcher_init( void * mem,
     last_header_id = header_id;
   }
   fd_h2_hdr_matcher_insert1( map, FD_H2_SEC_WEBSOCKET_KEY,        "sec-websocket-key",        17UL );
-  fd_h2_hdr_matcher_insert1( map, FD_H2_SEC_WEBSOCKET_EXTENSIONS, "sec-websocket-extensions", 25UL );
+  fd_h2_hdr_matcher_insert1( map, FD_H2_SEC_WEBSOCKET_EXTENSIONS, "sec-websocket-extensions", 24UL );
   fd_h2_hdr_matcher_insert1( map, FD_H2_SEC_WEBSOCKET_PROTOCOL,   "sec-websocket-protocol",   22UL );
   fd_h2_hdr_matcher_insert1( map, FD_H2_SEC_WEBSOCKET_ACCEPT,     "sec-websocket-accept",     20UL );
   fd_h2_hdr_matcher_insert1( map, FD_H2_SEC_WEBSOCKET_VERSION,    "sec-websocket-version",    21UL );
```

### src/waltz/h2/test_h2_hdr_match.c
```diff
@@ -102,7 +102,7 @@ test_h2_hdr_match( void ) {
   }
 
   FD_TEST( fd_h2_hdr_match( matcher, "sec-websocket-key",        17UL, 0U )==-53 );
-  FD_TEST( fd_h2_hdr_match( matcher, "sec-websocket-extensions", 25UL, 0U )==-54 );
+  FD_TEST( fd_h2_hdr_match( matcher, "sec-websocket-extensions", 24UL, 0U )==-54 );
   FD_TEST( fd_h2_hdr_match( matcher, "sec-websocket-accept",     20UL, 0U )==-55 );
   FD_TEST( fd_h2_hdr_match( matcher, "sec-websocket-protocol",   22UL, 0U )==-56 );
   FD_TEST( fd_h2_hdr_match( matcher, "sec-websocket-version",    21UL, 0U )==-57 );
```
