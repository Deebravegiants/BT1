# [?] fixed overflow

## Summary
Severity: Unknown
Chain: EigenLayer
Component: Layr-Labs/eigenlayer-contracts
Published: 2023-05-24
Source: https://github.com/Layr-Labs/eigenlayer-contracts/commit/a533f2ef1a09b1630afe85aa2b4ab3b8219e3d11
Type: security-commit

## Details
fixed overflow

## Patch
### src/contracts/middleware/BLSPubkeyRegistry.sol
```diff
@@ -8,8 +8,10 @@ import "../interfaces/IBLSPublicKeyCompendium.sol";
 
 import "../libraries/BN254.sol";
 
+import "forge-std/Test.sol";
 
-contract BLSPubkeyRegistry is IBLSPubkeyRegistry {
+
+contract BLSPubkeyRegistry is IBLSPubkeyRegistry, Test {
 
     BN254.G1Point internal _globalApk;
 
@@ -49,6 +51,7 @@ contract BLSPubkeyRegistry is IBLSPubkeyRegistry {
         pubkeyCompendium = _pubkeyCompendium;
 
         _initializeApkUpdates();
+        emit log("here");
 
     }
 
@@ -135,12 +138,11 @@ contract BLSPubkeyRegistry is IBLSPubkeyRegistry {
         return uint32(globalApkUpdateList.length);
     }
 
-
-
-
     function _processGlobalApkUpdate(BN254.G1Point memory newGlobalApk) internal returns(bytes32){
         bytes32 globalApkHash = BN254.hashG1Point(newGlobalApk);
-        globalApkUpdateList[globalApkUpdateList.length - 1].nextUpdateBlockNumber = uint32(block.number);
+        if(globalApkUpdateList.length > 0){
+            globalApkUpdateList[globalApkUpdateList.length - 1].nextUpdateBlockNumber = uint32(block.number);
+        }
         _globalApk = newGlobalApk;
 
         ApkUpdate memory latestGlobalApkUpdate;
@@ -177,16 +179,25 @@ contract BLSPubkeyRegistry is IBLSPubkeyRegistry {
     }
 
     function _initializeApkUpdates() internal {
+
         BN254.G1Point memory pk = BN254.G1Point(0,0);
         _processGlobalApkUpdate(pk);
 
-        for (uint8 quorumNumber = 0; quorumNumber < 256; quorumNumber++) {
+        for (uint8 quorumNumber = 0; quorumNumber < 255; quorumNumber++) {
+
             quorumToApk[quorumNumber] = pk;
             quorumToApkUpdates[quorumNumber].push(ApkUpdate({
                 apkHash: BN254.hashG1Point(pk),
                 updateBlockNumber: uint32(block.number),
                 nextUpdateBlockNumber: 0
             }));
         }
+        quorumToApk[255] = pk;
+        quorumToApkUpdates[255].push(ApkUpdate({
+            apkHash: BN254.hashG1Point(pk),
+            updateBlockNumber: uint32(block.number),
+            nextUpdateBlockNumber: 0
+        }));
+
     }
 }
\ No newline at end of file
```
