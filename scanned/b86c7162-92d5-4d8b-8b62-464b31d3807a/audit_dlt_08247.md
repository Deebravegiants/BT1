# [?] Fix crash when ipecho traffic blocked by iptables

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-08
Source: https://github.com/firedancer-io/firedancer/commit/33642b819f741a7c938f91e5d74104a0d035f863
Type: security-commit

## Details
Fix crash when ipecho traffic blocked by iptables

Linux netfilter can cause network operations to return EPERM.

## Patch
### src/discof/ipecho/fd_ipecho_server.c
```diff
@@ -213,7 +213,9 @@ is_expected_network_error( int err ) {
     err==ENETRESET ||
     err==ECONNABORTED ||
     err==ECONNRESET ||
-    err==EPIPE;
+    err==EPIPE ||
+    err==EPERM || /* iptables */
+    err==ENOMEM; /* net stack OOM */
 }
 
 static void
```

### src/waltz/http/fd_http_server.c
```diff
@@ -394,7 +394,9 @@ is_expected_network_error( int err ) {
     err==ENETRESET ||
     err==ECONNABORTED ||
     err==ECONNRESET ||
-    err==EPIPE;
+    err==EPIPE ||
+    err==EPERM || /* iptables */
+    err==ENOMEM; /* net stack OOM */
 }
 
 static void
```
