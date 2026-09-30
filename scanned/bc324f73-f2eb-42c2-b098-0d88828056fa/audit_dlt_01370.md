# [?] fix: 20146: Bucket.keyEquals() may throw an underflow exception (#20147)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2025-07-11
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/e052a0ff9d80bc27940c04f0832dafdf0a910554
Type: security-commit

## Details
fix: 20146: Bucket.keyEquals() may throw an underflow exception (#20147)

Fixes: https://github.com/hiero-ledger/hiero-consensus-node/issues/20146
Reviewed-by: Ivan Malygin <ivan@swirldslabs.com>, Oleg Mazurov <oleg.mazurov@swirldslabs.com>
Signed-off-by: Artem Ananev <artem.ananev@swirldslabs.com>

## Patch
### platform-sdk/swirlds-merkledb/src/main/java/com/swirlds/merkledb/files/hashmap/Bucket.java
```diff
@@ -484,6 +484,9 @@ private FindResult findEntry(final int keyHashCode, final Bytes key) {
     }
 
     private boolean keyEquals(final long pos, final int size, final Bytes key) {
+        if (size != key.length()) {
+            return false;
+        }
         for (int i = 0; i < size; i++) {
             if (bucketData.getByte(pos + i) != key.getByte(i)) {
                 return false;
```

### platform-sdk/swirlds-merkledb/src/test/java/com/swirlds/merkledb/files/hashmap/BucketTest.java
```diff
@@ -6,6 +6,7 @@
 import static org.junit.jupiter.api.Assertions.assertEquals;
 
 import com.hedera.pbj.runtime.io.buffer.BufferedData;
+import com.hedera.pbj.runtime.io.buffer.Bytes;
 import com.swirlds.merkledb.test.fixtures.ExampleLongKeyFixedSize;
 import com.swirlds.merkledb.test.fixtures.ExampleLongKeyVariableSize;
 import com.swirlds.virtualmap.VirtualKey;
@@ -285,6 +286,48 @@ void parsedBucketPutIfEqual(final KeyType keyType) throws IOException {
                 () -> bucket.putValue(keyType.keySerializer.toBytes(key1), key1.hashCode(), INVALID_VALUE, 1));
     }
 
+    @Test
+    void keyEqualsKeyTooShortTest() throws IOException {
+        final Bytes keyInBucket = Bytes.wrap(new byte[] {1, 2, 3, 4});
+        final Bytes keyToSearch = Bytes.wrap(new byte[] {1, 2});
+        // Let's pretend both keys have the same hash code
+        final int hashCode = 111;
+        final int value = 1;
+        try (final Bucket bucket = new Bucket()) {
+            bucket.putValue(keyInBucket, hashCode, value);
+            assertEquals(value, bucket.findValue(hashCode, keyInBucket, -1));
+            assertEquals(-1, bucket.findValue(hashCode, keyToSearch, -1));
+        }
+    }
+
+    @Test
+    void keyEqualsKeyTooLongTest() throws IOException {
+        final Bytes keyInBucket = Bytes.wrap(new byte[] {1, 2, 3, 4});
+        final Bytes keyToSearch = Bytes.wrap(new byte[] {1, 2, 3, 4, 5, 6});
+        // Let's pretend both keys have the same hash code
+        final int hashCode = 111;
+        final int value = 1;
+        try (final Bucket bucket = new Bucket()) {
+            bucket.putValue(keyInBucket, hashCode, value);
+            assertEquals(value, bucket.findValue(hashCode, keyInBucket, -1));
+            assertEquals(-1, bucket.findValue(hashCode, keyToSearch, -1));
+        }
+    }
+
+    @Test
+    void keyEqualsKeyEmptyTest() throws IOException {
+        final Bytes keyInBucket = Bytes.wrap(new byte[] {1, 2, 3, 4});
+        final Bytes keyToSearch = Bytes.wrap(new byte[0]);
+        // Let's pretend both keys have the same hash code
+        final int hashCode = 111;
+        final int value = 1;
+        try (final Bucket bucket = new Bucket()) {
+            bucket.putValue(keyInBucket, hashCode, value);
+            assertEquals(value, bucket.findValue(hashCode, keyInBucket, -1));
+            assertEquals(-1, bucket.findValue(hashCode, keyToSearch, -1));
+        }
+    }
+
     private void checkKey(KeyType keyType, Bucket bucket, VirtualKey key) {
         var findResult = assertDoesNotThrow(
                 () -> bucket.findValue(key.hashCode(), keyType.keySerializer.toBytes(key), -1),
```
