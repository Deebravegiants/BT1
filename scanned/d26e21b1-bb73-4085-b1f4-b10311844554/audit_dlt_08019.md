# [?] 9839 Prevented possible NPE caused by a race condition (#9840)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2023-11-13
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/f2869d915475cff7becf616b92a33ea1155b5098
Type: security-commit

## Details
9839 Prevented possible NPE caused by a race condition (#9840)

Signed-off-by: Ivan Malygin <ivan@swirldslabs.com>

## Patch
### platform-sdk/swirlds-jasperdb/src/main/java/com/swirlds/merkledb/files/DataFileCollection.java
```diff
@@ -489,6 +489,9 @@ protected D readDataItem(final long dataLocation) throws IOException {
             return null;
         }
         final ByteBuffer dataItemBytes = file.readDataItemBytes(dataLocation);
+        if (dataItemBytes == null) {
+            return null;
+        }
         return dataItemSerializer.deserialize(dataItemBytes, file.getMetadata().getSerializationVersion());
     }
 
```

### platform-sdk/swirlds-jasperdb/src/main/java/com/swirlds/merkledb/files/DataFileReader.java
```diff
@@ -186,6 +186,9 @@ ByteBuffer readDataItemBytes(final long dataLocation) throws IOException {
         if (dataItemSerializer.isVariableSize()) {
             // read header to get size
             final ByteBuffer serializedHeader = read(byteOffset, dataItemSerializer.getHeaderSize());
+            if (serializedHeader == null) {
+                return null;
+            }
             final DataItemHeader header = dataItemSerializer.deserializeHeader(serializedHeader);
             bytesToRead = header.getSizeBytes();
         } else {
@@ -376,6 +379,11 @@ private ByteBuffer read(final long byteOffsetInFile, final int bytesToRead) thro
         for (int retries = 3; retries > 0; retries--) {
             final int fcIndex = leaseFileChannel();
             final FileChannel fileChannel = fileChannels.get(fcIndex);
+            if (fileChannel == null) {
+                // On rare occasions, if we have a race condition with compaction, the file channel
+                // may be closed. We need to return null, so that the caller can retry with a new reader
+                return null;
+            }
             try {
                 buffer.position(0);
                 buffer.limit(bytesToRead);
```
