# [?] Fix a race condition with rpc ports in check-seeds

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-02-11
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/7f63be6a4ba64becdaac23a2d930e85d1c6ab26e
Type: security-commit

## Details
Fix a race condition with rpc ports in check-seeds

Summary:
The RPC port from the first run of test-seeds is not guaranteed to be closed/cleaned up
by the OS by the time the second run on test-seeds occurs.  Without this patch, check-seeds is flaky
and fails at random.

Test Plan:
```
ABC_BUILD_NAME=check-seeds ./build-configuration.sh
```
Run this a few times on CI too

Reviewers: #bitcoin_abc, Fabien

Reviewed By: #bitcoin_abc, Fabien

Differential Revision: https://reviews.bitcoinabc.org/D5268

## Patch
### contrib/seeds/test-seeds.sh
```diff
@@ -9,6 +9,7 @@ set -u
 
 TOPLEVEL=$(git rev-parse --show-toplevel)
 DEFAULT_BUILD_DIR="${TOPLEVEL}/build"
+DEFAULT_RPC_PORT=18832
 
 help_message() {
   echo "Test connecting to seed nodes. Outputs the seeds that were successfully connected to."
@@ -23,6 +24,7 @@ help_message() {
   echo ""
   echo "Environment Variables:"
   echo "BUILD_DIR             Default: ${DEFAULT_BUILD_DIR}"
+  echo "RPC_PORT              Default: ${DEFAULT_RPC_PORT}"
   exit 0
 }
 
@@ -60,8 +62,9 @@ if [ ! -x "${BITCOIN_CLI}" ]; then
 fi
 
 TEMP_DATADIR=$(mktemp -d)
-BITCOIND="${BITCOIND} -datadir=${TEMP_DATADIR} ${OPTION_TESTNET} -rpcport=18832 -connect=0 -daemon"
-BITCOIN_CLI="${BITCOIN_CLI} -datadir=${TEMP_DATADIR} ${OPTION_TESTNET} -rpcport=18832"
+: "${RPC_PORT:=${DEFAULT_RPC_PORT}}"
+BITCOIND="${BITCOIND} -datadir=${TEMP_DATADIR} ${OPTION_TESTNET} -rpcport=${RPC_PORT} -connect=0 -daemon"
+BITCOIN_CLI="${BITCOIN_CLI} -datadir=${TEMP_DATADIR} ${OPTION_TESTNET} -rpcport=${RPC_PORT}"
 
 >&2 echo "Spinning up bitcoind..."
 ${BITCOIND} || {
```

### contrib/teamcity/build-configurations.sh
```diff
@@ -254,8 +254,10 @@ case "$ABC_BUILD_NAME" in
 
   check-seeds)
     "${CI_SCRIPTS_DIR}"/build_cmake.sh
-    "${CI_SCRIPTS_DIR}"/check-seeds.sh main 80
-    "${CI_SCRIPTS_DIR}"/check-seeds.sh test 70
+    # Run on different ports to avoid a race where the rpc port used in the
+    # first run may not be closed in time for the second to start.
+    RPC_PORT=18832 "${CI_SCRIPTS_DIR}"/check-seeds.sh main 80
+    RPC_PORT=18833 "${CI_SCRIPTS_DIR}"/check-seeds.sh test 70
     ;;
 
   *)
```
