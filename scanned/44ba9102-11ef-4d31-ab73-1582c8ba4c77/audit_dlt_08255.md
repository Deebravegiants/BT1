# [?] gui: fix oob read (#9681)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-08
Source: https://github.com/firedancer-io/firedancer/commit/199dd5db7c00642cedae7540a21649e19a0ac483
Type: security-commit

## Details
gui: fix oob read (#9681)

## Patch
### src/disco/gui/fd_gui_printf.c
```diff
@@ -2342,7 +2342,11 @@ fd_gui_printf_peers_viewport_update( fd_gui_peers_ctx_t *  peers,
             jsonp_open_object( peers->http, NULL );
               jsonp_ulong ( peers->http, "row_index", j );
               jsonp_string( peers->http, "column_name", "Country" );
-              jsonp_string( peers->http, "new_value", peers->dbip.country_code[ cur->country_code_idx ] );
+              if( FD_LIKELY( cur->country_code_idx!=UCHAR_MAX ) ) {
+                jsonp_string( peers->http, "new_value", peers->dbip.country_code[ cur->country_code_idx ] );
+              } else {
+                jsonp_null( peers->http, "new_value" );
+              }
             jsonp_close_object( peers->http );
           }
 
@@ -2446,7 +2450,11 @@ fd_gui_printf_peers_viewport_request( fd_gui_peers_ctx_t *  peers,
           fd_base58_encode_32( cur->pubkey.uc, NULL, pubkey_base58 );
           jsonp_string( peers->http, "Pubkey", pubkey_base58 );
           jsonp_string( peers->http, "Name", cur->name );
-          jsonp_string( peers->http, "Country", peers->dbip.country_code[ cur->country_code_idx ] );
+          if( FD_LIKELY( cur->country_code_idx!=UCHAR_MAX ) ) {
+            jsonp_string( peers->http, "Country", peers->dbip.country_code[ cur->country_code_idx ] );
+          } else {
+            jsonp_null( peers->http, "Country" );
+          }
 
           uint ip4 = cur->contact_info.sockets[ FD_GOSSIP_CONTACT_INFO_SOCKET_GOSSIP ].is_ipv6 ? 0U : cur->contact_info.sockets[ FD_GOSSIP_CONTACT_INFO_SOCKET_GOSSIP ].ip4;
           char peer_addr[ 16 ]; /* 255.255.255.255 + '\0' */
```
