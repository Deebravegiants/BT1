# [?] LocalSecret: Fix CORS proxy crashing after a container restart

## Summary
Severity: Unknown
Chain: Secret
Component: scrtlabs/SecretNetwork
Published: 2023-01-19
Source: https://github.com/scrtlabs/SecretNetwork/commit/bac76c3b348560f5688b1f6fe993622b33218821
Type: security-commit

## Details
LocalSecret: Fix CORS proxy crashing after a container restart

## Patch
### deployment/docker/localsecret/bootstrap_init_no_stop.sh
```diff
@@ -55,18 +55,16 @@ then
   secretd collect-gentxs
   secretd validate-genesis
 
-#  secretd init-enclave
   secretd init-bootstrap
-#  cp new_node_seed_exchange_keypair.sealed .sgx_sec rets
   secretd validate-genesis
-fi
 
-# Setup CORS for LCD & gRPC-web
-perl -i -pe 's;address = "tcp://0.0.0.0:1317";address = "tcp://0.0.0.0:1316";' ~/.secretd/config/app.toml
-perl -i -pe 's/enable-unsafe-cors = false/enable-unsafe-cors = true/' ~/.secretd/config/app.toml
-perl -i -pe 's/concurrency = false/concurrency = true/' ~/.secretd/config/app.toml
+  # Setup LCD
+  perl -i -pe 's;address = "tcp://0.0.0.0:1317";address = "tcp://0.0.0.0:1316";' ~/.secretd/config/app.toml
+  perl -i -pe 's/enable-unsafe-cors = false/enable-unsafe-cors = true/' ~/.secretd/config/app.toml
+  perl -i -pe 's/concurrency = false/concurrency = true/' ~/.secretd/config/app.toml
+fi
 
-lcp --proxyUrl http://localhost:1316 --port 1317 --proxyPartial '' &
+setsid lcp --proxyUrl http://localhost:1316 --port 1317 --proxyPartial '' &
 
 if [ "${ENABLE_FAUCET}" = "true" ]; then
   # Setup faucet
```
