# [?] Fixes: GHSA-h552-3fxr-chmx Bound the storage sub-range split count in snap sync (#11094)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/c3a15f960c94723dee1e3c14577da2e6c01c9f70
Type: security-commit

## Details
Fixes: GHSA-h552-3fxr-chmx Bound the storage sub-range split count in snap sync (#11094)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -68,6 +68,7 @@
 
 ### Bug fixes
 - Improve logging for malformed discv4 UDP packets.
+- Bound the snap sync storage sub-range split count to prevent unbounded memory growth under a malformed snap response.
 - Remove `System.out`/`System.err` logging from `P256VerifyPrecompiledContract` and `BlockchainQueries` — these could leak sensitive data to stdout/stderr in production.
 - EIP-1459 DNS discovery now rejoins TXT records split across multiple `<character-string>`s. Records longer than 255 bytes were truncated, so Besu silently discarded most of every tree, resolving 832 of 3000 nodes from the mainnet tree. [#10985](https://github.com/besu-eth/besu/pull/10985)
 - Queue backward-sync targets received before peer readiness and retry when a peer connects. [#10843](https://github.com/besu-eth/besu/pull/10843)
```

### ethereum/eth/src/test/java/org/hyperledger/besu/ethereum/eth/sync/snapsync/RangeManagerTest.java
```diff
@@ -58,6 +58,53 @@ public void testRemainingRangesEqualToOneWhenFirstRangeContainsLessThanHalf() {
     assertThat(nbRanges).isEqualTo(2);
   }
 
+  @Test
+  public void testGetRangeCountIsClampedWhenLastKeyIsTiny() {
+    // A peer returns a partial range whose largest slot hash has many leading zero bits
+    // (here bit 230 set, everything below it zero). The raw division
+    // MAX_RANGE / lastKey is astronomically large (~2^26), which would otherwise be
+    // materialized as that many TreeMap ranges/child requests -> OutOfMemoryError.
+    final TreeMap<Bytes32, Bytes> items = new TreeMap<>();
+    items.put(toBytes32(BigInteger.TWO.pow(230)), Bytes.wrap(new byte[] {0x03}));
+    final int nbRanges =
+        RangeManager.getRangeCount(RangeManager.MIN_RANGE, RangeManager.MAX_RANGE, items);
+    assertThat(nbRanges).isBetween(1, RangeManager.MAX_RANGE_COUNT);
+  }
+
+  @Test
+  public void testGetRangeCountIsNeverNegativeOnIntOverflow() {
+    // A peer returns a partial range whose largest slot hash is 2^224. The raw division yields
+    // 2^32 - 1 (0xFFFFFFFF). The count must stay a sane positive value.
+    final TreeMap<Bytes32, Bytes> items = new TreeMap<>();
+    items.put(toBytes32(BigInteger.TWO.pow(224)), Bytes.wrap(new byte[] {0x03}));
+    final int nbRanges =
+        RangeManager.getRangeCount(RangeManager.MIN_RANGE, RangeManager.MAX_RANGE, items);
+    assertThat(nbRanges).isBetween(1, RangeManager.MAX_RANGE_COUNT);
+  }
+
+  @Test
+  public void testGetRangeCountWhenNoKeysReturned() {
+    // findNewBeginElementInRange can report a missing element even when the peer returned zero
+    // keys (proofs alone resolve in-range leaves). getRangeCount is called with that empty map, so
+    // it must not dereference items.lastKey() (which would throw NoSuchElementException) and should
+    // fall back to a single follow-up range.
+    final int nbRanges =
+        RangeManager.getRangeCount(RangeManager.MIN_RANGE, RangeManager.MAX_RANGE, new TreeMap<>());
+    assertThat(nbRanges).isEqualTo(1);
+  }
+
+  @Test
+  public void testGetRangeCountWhenLastKeyEqualsRangeStart() {
+    // A peer whose only returned key is the range start (0x00..00) gives a zero-width divisor.
+    // The raw MAX_RANGE / (lastKey - min) would divide by zero -> ArithmeticException; the count
+    // must instead degrade to a single follow-up range.
+    final TreeMap<Bytes32, Bytes> items = new TreeMap<>();
+    items.put(RangeManager.MIN_RANGE, Bytes.wrap(new byte[] {0x03}));
+    final int nbRanges =
+        RangeManager.getRangeCount(RangeManager.MIN_RANGE, RangeManager.MAX_RANGE, items);
+    assertThat(nbRanges).isEqualTo(1);
+  }
+
   @Test
   public void testGenerateAllRangesWithSize1() {
     final Map<Bytes32, Bytes32> expectedResult = new HashMap<>();
@@ -363,6 +410,10 @@ public void testGenerateRangesStartsWithMin() {
     assertThat(singleRange.entrySet().iterator().next().getKey()).isEqualTo(bytesMin);
   }
 
+  private static Bytes32 toBytes32(final BigInteger value) {
+    return Bytes32.leftPad(Bytes.wrap(value.toByteArray()).trimLeadingZeros());
+  }
+
   private static void assertKeysAreStrictlyIncreasing(final Map<Bytes32, Bytes32> ranges) {
     Bytes32 previousKey = null;
     for (final Bytes32 key : ranges.keySet()) {
```

### ethereum/trie/src/main/java/org/hyperledger/besu/ethereum/trie/RangeManager.java
```diff
@@ -39,20 +39,41 @@
  */
 public class RangeManager {
 
-  public static final Bytes32 MIN_RANGE = Bytes32.wrap(Hash.wrap(Bytes32.ZERO).getBytes());
+  public static final Bytes32 MIN_RANGE = Bytes32.ZERO;
   public static final Bytes32 MAX_RANGE =
-      Bytes32.wrap(
-          Hash.fromHexString("0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
-              .getBytes());
+      Bytes32.fromHexString("0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
+
+  public static final BigInteger MAX_RANGE_BIG_INTEGER = MAX_RANGE.toUnsignedBigInteger();
+
+  /**
+   * Upper bound on the number of sub-ranges {@link #getRangeCount} will ever return, preventing an
+   * unbounded (or, after {@code int} truncation, negative) split count from a peer that returns a
+   * partial range whose largest key has many leading zero bits.
+   */
+  public static final int MAX_RANGE_COUNT = 16;
 
   private RangeManager() {}
 
   public static int getRangeCount(
       final Bytes32 min, final Bytes32 max, final NavigableMap<Bytes32, Bytes> items) {
     if (min.equals(MIN_RANGE) && max.equals(MAX_RANGE)) {
-      return MAX_RANGE
-          .toUnsignedBigInteger()
-          .divide(items.lastKey().toUnsignedBigInteger().subtract(min.toUnsignedBigInteger()))
+      // items may be empty (findNewBeginElementInRange can report a missing element from proofs
+      // alone), so guard before dereferencing lastKey().
+      if (items.isEmpty()) {
+        return 1;
+      }
+      final BigInteger lastKey = items.lastKey().toUnsignedBigInteger();
+      if (lastKey.signum() == 0) {
+        // A largest key of zero would make the division throw; degrade to a single follow-up range.
+        return 1;
+      }
+      // Clamp with BigInteger arithmetic before narrowing: the raw quotient can far exceed
+      // Integer.MAX_VALUE for a tiny divisor, and BigInteger.intValue() would silently truncate it
+      // to a huge or negative int. Bounding it to [1, MAX_RANGE_COUNT] keeps it safely narrowable.
+      return MAX_RANGE_BIG_INTEGER
+          .divide(lastKey)
+          .max(BigInteger.ONE)
+          .min(BigInteger.valueOf(MAX_RANGE_COUNT))
           .intValue();
     }
     return 1;
@@ -62,8 +83,7 @@ public static Map<Bytes32, Bytes32> generateAllRanges(final int sizeRange) {
     if (sizeRange == 1) {
       return Map.ofEntries(Map.entry(MIN_RANGE, MAX_RANGE));
     }
-    return generateRanges(
-        MIN_RANGE.toUnsignedBigInteger(), MAX_RANGE.toUnsignedBigInteger(), sizeRange);
+    return generateRanges(BigInteger.ZERO, MAX_RANGE_BIG_INTEGER, sizeRange);
   }
 
   /**
```
