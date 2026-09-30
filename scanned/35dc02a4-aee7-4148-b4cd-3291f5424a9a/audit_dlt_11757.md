# [?] ops: Fix install script crash for removed electrs-start-liquidtestnet

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2023-08-17
Source: https://github.com/mempool/mempool/commit/f1f97320dfa41f2c798bf974a6cb09a1e33168dd
Type: security-commit

## Details
ops: Fix install script crash for removed electrs-start-liquidtestnet

## Patch
### production/install
```diff
@@ -1641,19 +1641,11 @@ fi
 ################################################
 
 if [ "${ELEMENTS_LIQUIDTESTNET_ENABLE}" = ON ];then
-    echo "[*] Installing Elements Liquid Testnet electrs start script"
-    osSudo "${ROOT_USER}" install -c -o "${ELEMENTS_USER}" -g "${ELEMENTS_GROUP}" -m 755 "${MEMPOOL_HOME}/${MEMPOOL_REPO_NAME}/production/electrs-start-liquidtestnet" "${ELEMENTS_ELECTRS_HOME}"
-
     echo "[*] Installing Elements Liquid Testnet RPC credentials"
     osSudo "${ROOT_USER}" sed -i.orig "s/__BITCOIN_RPC_USER__/${BITCOIN_RPC_USER}/" "${ELEMENTS_HOME}/elements.conf"
     osSudo "${ROOT_USER}" sed -i.orig "s/__BITCOIN_RPC_PASS__/${BITCOIN_RPC_PASS}/" "${ELEMENTS_HOME}/elements.conf"
     osSudo "${ROOT_USER}" sed -i.orig "s/__ELEMENTS_RPC_USER__/${ELEMENTS_RPC_USER}/" "${ELEMENTS_HOME}/elements.conf"
     osSudo "${ROOT_USER}" sed -i.orig "s/__ELEMENTS_RPC_PASS__/${ELEMENTS_RPC_PASS}/" "${ELEMENTS_HOME}/elements.conf"
-
-    echo "[*] Configuring Elements LiquidTestnet RPC credentials in electrs start script"
-    osSudo "${ROOT_USER}" sed -i.orig "s/__ELEMENTS_RPC_USER__/${ELEMENTS_RPC_USER}/" "${ELEMENTS_ELECTRS_HOME}/electrs-start-liquidtestnet"
-    osSudo "${ROOT_USER}" sed -i.orig "s/__ELEMENTS_RPC_PASS__/${ELEMENTS_RPC_PASS}/" "${ELEMENTS_ELECTRS_HOME}/electrs-start-liquidtestnet"
-    osSudo "${ROOT_USER}" sed -i.orig "s!__ELECTRS_DATA_ROOT__!${ELECTRS_DATA_ROOT}!" "${ELEMENTS_ELECTRS_HOME}/electrs-start-liquidtestnet"
 fi
 
 ################################
```
