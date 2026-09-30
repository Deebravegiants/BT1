# [?] tls: fix array layout in test leading to oob

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-05
Source: https://github.com/firedancer-io/firedancer/commit/cbc9537ec578c9b8c6229c4b30e57c56a42a066c
Type: security-commit

## Details
tls: fix array layout in test leading to oob

## Patch
### src/waltz/tls/test_tls_openssl.c
```diff
@@ -40,7 +40,11 @@ static uchar const tp_buf[] = { 0x01, 0x02, 0x47, 0xd0 };
 
 /* Save secrets */
 
-static uchar secret[ 32UL ][2][4][2] = {0};
+/* secret[ impl ][ level ][ direction ][ 32 ] where impl is 0 for fd_tls and
+   1 for OpenSSL, level is FD_TLS_LEVEL_{...}, and direction is 0 for recv
+   and 1 for send. */
+
+static uchar secret[2][4][2][ 32UL ] = {0};
 
 /* Track current OpenSSL encryption level for sending */
 static uint _ossl_send_level = FD_TLS_LEVEL_INITIAL;
```
