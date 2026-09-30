# [?] Prevent a potential panic on dereferencing a 'none' value

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2023-03-14
Source: https://github.com/status-im/nimbus-eth2/commit/d899a6a834c083a62e1246eade5027a7019ace82
Type: security-commit

## Details
Prevent a potential panic on dereferencing a 'none' value

## Patch
### beacon_chain/eth1/eth1_monitor.nim
```diff
@@ -1987,6 +1987,15 @@ proc syncEth1Chain(m: ELManager, connection: ELConnection) {.async.} =
   let rpcClient = awaitOrRaiseOnTimeout(connection.connectedRpcClient(),
                                         1.seconds)
   let
+    # BEWARE
+    # `connectedRpcClient` guarantees that connection.web3 will not be
+    # `none` here, but it's not safe to initialize this later (e.g closer
+    # to where it's used) because `connection.web3` may be set to `none`
+    # at any time after a failed request. Luckily, the `contractSender`
+    # object is very cheap to create.
+    depositContract = connection.web3.get.contractSender(
+      DepositContract, m.depositContractAddress)
+
     shouldProcessDeposits = not (
       m.depositContractAddress.isZeroMemory or
       m.eth1Chain.finalizedBlockHash.data.isZeroMemory)
@@ -2085,8 +2094,6 @@ proc syncEth1Chain(m: ELManager, connection: ELConnection) {.async.} =
 
     if shouldProcessDeposits and
        latestBlock.number.uint64 > m.cfg.ETH1_FOLLOW_DISTANCE:
-      let depositContract = connection.web3.get.contractSender(
-        DepositContract, m.depositContractAddress)
       await m.syncBlockRange(connection,
                              rpcClient,
                              depositContract,
```
