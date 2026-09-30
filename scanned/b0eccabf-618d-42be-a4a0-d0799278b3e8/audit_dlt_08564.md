# [?] Siphash24 in BinaryFuseFilter for DOS protection

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2024-07-17
Source: https://github.com/stellar/stellar-core/commit/ebef6c3687087685ae7422c2f56ae7c2f6ae0405
Type: security-commit

## Details
Siphash24 in BinaryFuseFilter for DOS protection

## Patch
### lib/binaryfusefilter.h
```diff
@@ -8,11 +8,17 @@
 #include <stdint.h>
 
 #include <algorithm>
+#include <array>
 #include <limits>
 #include <type_traits>
 #include <vector>
 
+#include "util/siphash.h"
+
 #include <Tracy.hpp>
+#include <sodium.h>
+
+typedef std::array<uint8_t, crypto_shorthash_KEYBYTES> binary_fuse_seed_t;
 
 #ifndef XOR_MAX_ITERATIONS
 #define XOR_MAX_ITERATIONS \
@@ -24,19 +30,11 @@
  * We start with a few utilities.
  ***/
 static inline uint64_t
-binary_fuse_murmur64(uint64_t h)
-{
-    h ^= h >> 33;
-    h *= UINT64_C(0xff51afd7ed558ccd);
-    h ^= h >> 33;
-    h *= UINT64_C(0xc4ceb9fe1a85ec53);
-    h ^= h >> 33;
-    return h;
-}
-static inline uint64_t
-binary_fuse_mix_split(uint64_t key, uint64_t seed)
+sip_hash24(uint64_t key, binary_fuse_seed_t const& seed)
 {
-    return binary_fuse_murmur64(key + seed);
+    SipHash24 hasher(seed.data());
+    hasher.update(reinterpret_cast<unsigned char*>(&key), sizeof(key));
+    return hasher.digest();
 }
 static inline uint64_t
 binary_fuse_rotl64(uint64_t n, unsigned int c)
@@ -212,7 +210,7 @@ template <typename T,
 class binary_fuse_t
 {
   private:
-    uint64_t _seed;
+    binary_fuse_seed_t _seed;
     uint32_t _segmentLength;
     uint32_t _segmentLengthMask;
     uint32_t _segmentCount;
@@ -294,7 +292,7 @@ class binary_fuse_t
     contain(uint64_t key) const
     {
         ZoneScoped;
-        uint64_t hash = binary_fuse_mix_split(key, _seed);
+        uint64_t hash = sip_hash24(key, _seed);
         T f = binary_fuse_fingerprint(hash);
         binary_hashes_t hashes = hash_batch(hash);
         f ^= _fingerprints[hashes.h0] ^ _fingerprints[hashes.h1] ^
@@ -317,7 +315,7 @@ class binary_fuse_t
     // which point the seed must be rotated. keys will be sorted and duplicates
     // removed if any duplicate keys exist
     [[nodiscard]] bool
-    populate(std::vector<uint64_t>& keys, uint64_t rngSeed)
+    populate(std::vector<uint64_t>& keys, binary_fuse_seed_t rngSeed)
     {
         ZoneScoped;
         if (keys.size() > std::numeric_limits<uint32_t>::max())
@@ -328,7 +326,7 @@ class binary_fuse_t
         uint32_t size = keys.size();
         ZoneValue(static_cast<int64_t>(size));
 
-        _seed = binary_fuse_rng_splitmix64(&rngSeed);
+        _seed = rngSeed;
 
         std::vector<uint64_t> reverseOrder(size + 1);
         uint32_t capacity = _arrayLength;
@@ -369,7 +367,7 @@ class binary_fuse_t
             uint64_t maskblock = block - 1;
             for (uint32_t i = 0; i < size; i++)
             {
-                uint64_t hash = binary_fuse_murmur64(keys[i] + _seed);
+                uint64_t hash = sip_hash24(keys[i], _seed);
                 uint64_t segment_index = hash >> (64 - blockBits);
                 while (reverseOrder[startPos[segment_index]] != 0)
                 {
@@ -422,7 +420,8 @@ class binary_fuse_t
                 std::fill(t2count.begin(), t2count.end(), 0);
                 std::fill(t2hash.begin(), t2hash.end(), 0);
 
-                _seed = binary_fuse_rng_splitmix64(&rngSeed);
+                // Rotate seed deterministically
+                _seed[0]++;
                 continue;
             }
 
@@ -486,7 +485,9 @@ class binary_fuse_t
             std::fill_n(reverseOrder.begin(), size, 0);
             std::fill(t2count.begin(), t2count.end(), 0);
             std::fill(t2hash.begin(), t2hash.end(), 0);
-            _seed = binary_fuse_rng_splitmix64(&rngSeed);
+
+            // Rotate seed deterministically
+            _seed[0]++;
         }
 
         for (uint32_t i = size - 1; i < size; i--)
```

### src/util/BinaryFuseFilter.cpp
```diff
@@ -11,7 +11,7 @@ namespace stellar
 
 template <typename T, typename U>
 BinaryFuseFilter<T, U>::BinaryFuseFilter(LedgerKeySet const& keys,
-                                         BinaryFuseSeed const& seed)
+                                         binary_fuse_seed_t const& seed)
     : mFilter(keys.size()), mInputSeed(seed)
 {
     std::vector<size_t> hashes;
@@ -24,21 +24,29 @@ BinaryFuseFilter<T, U>::BinaryFuseFilter(LedgerKeySet const& keys,
         hashes.push_back(hasher.digest());
     }
 
-    for (size_t i = 0;; ++i)
+    // If too many hash collisions occur, population will fail. Retry with
+    // a different seed. This is unlikely to happen once, and is statically
+    // impossible to happen 10 times.
+    bool populated = false;
+    for (size_t i = 0; i < 10; ++i)
     {
-        //     auto filterSeed = mInputSeed;
-        //     filterSeed[0] += i;
-        //     if (mFilter.populate(hashes, filterSeed))
-        //     {
-        //         break;
-        //     }
-
-        // TODO: Seed for SipHash24
-        if (mFilter.populate(hashes, i))
+        auto filterSeed = mInputSeed;
+
+        // Arbitrary seed rotation if too many hash collisions occur during
+        // population. Library rotates filterSeed[0], so rotate filterSeed[1]
+        filterSeed[1] += i;
+        if (mFilter.populate(hashes, filterSeed))
         {
+            populated = true;
             break;
         }
     }
+
+    // Not statically possible
+    if (!populated)
+    {
+        throw std::runtime_error("BinaryFuseFilter failed to populate");
+    }
 }
 
 template <typename T, typename U>
```

### src/util/BinaryFuseFilter.h
```diff
@@ -7,13 +7,10 @@
 #include "lib/binaryfusefilter.h"
 #include "util/NonCopyable.h"
 #include "util/types.h"
-#include <sodium.h>
 
 namespace stellar
 {
 
-typedef std::array<uint8_t, crypto_shorthash_KEYBYTES> BinaryFuseSeed;
-
 // This class is a wrapper around the binary_fuse_t library that provides
 // serialization for the XDR BinaryFuseFilter type and provides a deterministic
 // LedgerKey interface.
@@ -29,14 +26,14 @@ class BinaryFuseFilter : public NonMovableOrCopyable
 
     // Note: as part of filter construction, the internal filter seed might
     // rotate and no longer be the same as the input seed. The input seed must
-    // be maintained outside of the filter and used to hash input keys to the
+    // be maintained outside of the filter and used to hash input keys in the
     // contain function to ensure deterministic hashing of input keys
     // during both populating and querying the filter.
-    BinaryFuseSeed const mInputSeed;
+    binary_fuse_seed_t const mInputSeed;
 
   public:
     explicit BinaryFuseFilter(LedgerKeySet const& keys,
-                              BinaryFuseSeed const& seed);
+                              binary_fuse_seed_t const& seed);
 
     bool contain(LedgerKey const& key) const;
 
```

### src/util/test/BinaryFuseTests.cpp
```diff
@@ -36,7 +36,7 @@ testFilter(double expectedFalsePositiveRate)
         }
 
         size_t randomMatches = 0;
-        size_t trials = 1'000'000;
+        size_t trials = 2'000'000;
         for (size_t i = 0; i < trials; i++)
         {
             LedgerKey randomKey;
@@ -59,9 +59,11 @@ testFilter(double expectedFalsePositiveRate)
         }
         else
         {
-            // False positive rate should be within 5% of the expected rate
+            // False positive rate should be within 15% of the expected rate
+            // The fpp is so small, we have to give a relatively large margin
+            // to account for float imprecision
             double fpp = randomMatches * 1.0 / trials;
-            double upperBound = expectedFalsePositiveRate * 1.05;
+            double upperBound = expectedFalsePositiveRate * 1.15;
             REQUIRE(fpp < upperBound);
         }
     }
```
