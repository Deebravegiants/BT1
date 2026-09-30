# [?] [docker-compose] Check docker logs separately to prevent race condition

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-03-03
Source: https://github.com/move-language/move/commit/7772e4dc1e3fdcceb960f7ade68b3956ac2bb8a8
Type: security-commit

## Details
[docker-compose] Check docker logs separately to prevent race condition

Closes: #7802

## Patch
### docker/compose/test_docker_compose.sh
```diff
@@ -2,7 +2,7 @@
 # Copyright (c) The Diem Core Contributors
 # SPDX-License-Identifier: Apache-2.0
 
-set timeout 5
+set timeout 10
 
 set basedir [file normalize [file dirname $argv0]]
 cd $basedir
@@ -17,13 +17,35 @@ expect_before {
 
 send "cd validator-testnet\r"
 send "docker-compose up --remove-orphans\r"
-# Order is non-deterministic, so we test both ways
-expect {
-  "validator_1*Diem is running" { expect  "faucet_1*running" }
-  "faucet_1*running*" { expect "validator_1*Diem is running" }
+
+sleep 10
+
+### Ensure validator is started
+spawn /bin/bash
+cd $basedir
+expect_before {
+    timeout { puts "\rERROR: Timeout!\r"; exit 1 }
+    eof { puts "\rERROR: eof!\r"; exit 1 }
 }
+send "cd validator-testnet\r"
+send "docker-compose logs -f validator\r"
+expect "validator_1*Diem is running"
+
+
+### Ensure faucet is started
+spawn /bin/bash
+cd $basedir
+expect_before {
+    timeout { puts "\rERROR: Timeout!\r"; exit 1 }
+    eof { puts "\rERROR: eof!\r"; exit 1 }
+}
+
+send "cd validator-testnet\r"
+send "docker-compose logs -f faucet\r"
+expect "faucet_1*running*"
+
 
-sleep 3
+sleep 5
 
 ### Test the CLI client
 spawn /bin/bash
```
