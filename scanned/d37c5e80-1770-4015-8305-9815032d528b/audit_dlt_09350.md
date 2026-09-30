# [?] Fix method handler crashed (#5905)

## Summary
Severity: Unknown
Chain: Tooling
Component: web3/web3.js
Published: 2023-03-08
Source: https://github.com/web3/web3.js/commit/c8ddaa26ea126f1c4e01396502bd59a13d2070b8
Type: security-commit

## Details
Fix method handler crashed (#5905)

* version fix

* use geth binary

* try 1.11.2

## Patch
### scripts/geth.sh
```diff
@@ -12,12 +12,12 @@ start() {
 	if [ -z "${ORIGARGS[1]}" ]
 	then
 		echo "Starting geth..."
-		echo "docker run -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:stable --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev"
-        docker run -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:stable --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev
+		echo "docker run -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:v1.11.2 --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev"
+        docker run -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:v1.11.2 --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev
 	else
 		echo "Starting geth..."
-		echo "docker run -d -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:stable --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev"
-        docker run -d -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:stable --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev
+		echo "docker run -d -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:v1.11.2 --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev"
+        docker run -d -p $WEB3_SYSTEM_TEST_PORT:$WEB3_SYSTEM_TEST_PORT ethereum/client-go:v1.11.2 --nodiscover --nousb --ws --ws.addr 0.0.0.0 --ws.port $WEB3_SYSTEM_TEST_PORT --http --http.addr 0.0.0.0 --http.port $WEB3_SYSTEM_TEST_PORT --allow-insecure-unlock --http.api personal,web3,eth,admin,debug,txpool,net --ws.api personal,web3,eth,admin,debug,miner,txpool,net --dev
 		echo "Waiting for geth..."
 		npx wait-port -t 10000 "$WEB3_SYSTEM_TEST_PORT"
 		echo "Geth started"
```
