# [?] Use Uint256 instead of long to avoid overflow (#9093)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2025-08-21
Source: https://github.com/besu-eth/besu/commit/2cff7d226a2da882860261c6187bed5a49eda7dc
Type: security-commit

## Details
Use Uint256 instead of long to avoid overflow (#9093)

Signed-off-by: Gabriel-Trintinalia <gabriel.trintinalia@consensys.net>

## Patch
### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/OsakaTargetingGasLimitCalculator.java
```diff
@@ -21,6 +21,8 @@
 import org.hyperledger.besu.ethereum.mainnet.feemarket.BaseFeeMarket;
 import org.hyperledger.besu.evm.gascalculator.GasCalculator;
 
+import org.apache.tuweni.units.bigints.UInt256;
+
 public class OsakaTargetingGasLimitCalculator extends CancunTargetingGasLimitCalculator {
   /** The constant max number of blobs per transaction defined for Osaka */
   private static final int DEFAULT_MAX_BLOBS_PER_TRANSACTION = 6;
@@ -86,9 +88,15 @@ public long computeExcessBlobGas(
     }
 
     // EIP-7918 https://eips.ethereum.org/EIPS/eip-7918
-    Wei baseFeeBlobGas = feeMarket.blobGasPricePerGas(BlobGas.of(parentExcessBlobGas));
-    long baseFeeBlobGasLong = baseFeeBlobGas.toLong();
-    if (BLOB_BASE_COST * parentBaseFeePerGas > getBlobGasPerBlob() * baseFeeBlobGasLong) {
+    Wei blobGasBaseFee = feeMarket.blobGasPricePerGas(BlobGas.of(parentExcessBlobGas));
+
+    UInt256 parentBaseFee = UInt256.valueOf(parentBaseFeePerGas);
+    UInt256 blobGasPerBlob = UInt256.valueOf(getBlobGasPerBlob());
+
+    UInt256 baseFeeCostPerBlob = parentBaseFee.multiply(UInt256.valueOf(BLOB_BASE_COST));
+    UInt256 effectiveBlobGasCost = blobGasBaseFee.toUInt256().multiply(blobGasPerBlob);
+
+    if (baseFeeCostPerBlob.compareTo(effectiveBlobGasCost) > 0) {
       return parentExcessBlobGas
           + parentBlobGasUsed * (maxBlobsPerBlock - targetBlobsPerBlock) / maxBlobsPerBlock;
     } else {
```
