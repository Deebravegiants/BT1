# [?] p2p: fix GCC 9.1 crash

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-06-08
Source: https://github.com/monero-project/monero/commit/2cbe75661cb957f7be409a9e22df97d96329c5c8
Type: security-commit

## Details
p2p: fix GCC 9.1 crash

## Patch
### src/p2p/net_peerlist_boost_serialization.h
```diff
@@ -134,10 +134,11 @@ namespace boost
       a & port;
       a & length;
 
-      if (length > net::tor_address::buffer_size())
+      const size_t buffer_size = net::tor_address::buffer_size();
+      if (length > buffer_size)
         MONERO_THROW(net::error::invalid_tor_address, "Tor address too long");
 
-      char host[net::tor_address::buffer_size()] = {0};
+      char host[buffer_size] = {0};
       a.load_binary(host, length);
       host[sizeof(host) - 1] = 0;
 
@@ -155,10 +156,11 @@ namespace boost
       a & port;
       a & length;
 
-      if (length > net::i2p_address::buffer_size())
+      const size_t buffer_size = net::i2p_address::buffer_size();
+      if (length > buffer_size)
         MONERO_THROW(net::error::invalid_i2p_address, "i2p address too long");
 
-      char host[net::i2p_address::buffer_size()] = {0};
+      char host[buffer_size] = {0};
       a.load_binary(host, length);
       host[sizeof(host) - 1] = 0;
 
```
