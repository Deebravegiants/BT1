# [?] util: introduce `TrySub` to prevent unsigned underflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-02-22
Source: https://github.com/bitcoin/bitcoin/commit/b8fa6f0f701f04cffca6a085337b508381016649
Type: security-commit

## Details
util: introduce `TrySub` to prevent unsigned underflow

Introduce `TrySub(T&, U)` which subtracts an unsigned integral `U` from an unsigned integral `T`, returning `false` on underflow.
Use with `Assume(TrySub(...))` at coins cache accounting decrement sites so invariant violations fail immediately rather than silently wrapping.

Co-authored-by: MarcoFalke <*~=`'#}+{/-|&$^_@721217.xyz>
Co-authored-by: Pieter Wuille <pieter@wuille.net>

## Patch
### src/coins.cpp
```diff
@@ -113,8 +113,8 @@ void CCoinsViewCache::AddCoin(const COutPoint &outpoint, Coin&& coin, bool possi
         fresh = !it->second.IsDirty();
     }
     if (!inserted) {
-        m_dirty_count -= it->second.IsDirty();
-        cachedCoinsUsage -= it->second.coin.DynamicMemoryUsage();
+        Assume(TrySub(m_dirty_count, it->second.IsDirty()));
+        Assume(TrySub(cachedCoinsUsage, it->second.coin.DynamicMemoryUsage()));
     }
     it->second.coin = std::move(coin);
     CCoinsCacheEntry::SetDirty(*it, m_sentinel);
@@ -153,8 +153,8 @@ void AddCoins(CCoinsViewCache& cache, const CTransaction &tx, int nHeight, bool
 bool CCoinsViewCache::SpendCoin(const COutPoint &outpoint, Coin* moveout) {
     CCoinsMap::iterator it = FetchCoin(outpoint);
     if (it == cacheCoins.end()) return false;
-    m_dirty_count -= it->second.IsDirty();
-    cachedCoinsUsage -= it->second.coin.DynamicMemoryUsage();
+    Assume(TrySub(m_dirty_count, it->second.IsDirty()));
+    Assume(TrySub(cachedCoinsUsage, it->second.coin.DynamicMemoryUsage()));
     TRACEPOINT(utxocache, spent,
            outpoint.hash.data(),
            (uint32_t)outpoint.n,
@@ -248,12 +248,12 @@ void CCoinsViewCache::BatchWrite(CoinsViewCacheCursor& cursor, const uint256& ha
             if (itUs->second.IsFresh() && it->second.coin.IsSpent()) {
                 // The grandparent cache does not have an entry, and the coin
                 // has been spent. We can just delete it from the parent cache.
-                m_dirty_count -= itUs->second.IsDirty();
-                cachedCoinsUsage -= itUs->second.coin.DynamicMemoryUsage();
+                Assume(TrySub(m_dirty_count, itUs->second.IsDirty()));
+                Assume(TrySub(cachedCoinsUsage, itUs->second.coin.DynamicMemoryUsage()));
                 cacheCoins.erase(itUs);
             } else {
                 // A normal modification.
-                cachedCoinsUsage -= itUs->second.coin.DynamicMemoryUsage();
+                Assume(TrySub(cachedCoinsUsage, itUs->second.coin.DynamicMemoryUsage()));
                 if (cursor.WillErase(*it)) {
                     // Since this entry will be erased,
                     // we can move the coin into us instead of copying it
@@ -311,7 +311,7 @@ void CCoinsViewCache::Uncache(const COutPoint& hash)
 {
     CCoinsMap::iterator it = cacheCoins.find(hash);
     if (it != cacheCoins.end() && !it->second.IsDirty()) {
-        cachedCoinsUsage -= it->second.coin.DynamicMemoryUsage();
+        Assume(TrySub(cachedCoinsUsage, it->second.coin.DynamicMemoryUsage()));
         TRACEPOINT(utxocache, uncache,
                hash.hash.data(),
                (uint32_t)hash.n,
```

### src/coins.h
```diff
@@ -15,6 +15,7 @@
 #include <support/allocators/pool.h>
 #include <uint256.h>
 #include <util/check.h>
+#include <util/overflow.h>
 #include <util/hasher.h>
 
 #include <cassert>
@@ -278,7 +279,7 @@ struct CoinsViewCacheCursor
     inline CoinsCachePair* NextAndMaybeErase(CoinsCachePair& current) noexcept
     {
         const auto next_entry{current.second.Next()};
-        m_dirty_count -= current.second.IsDirty();
+        Assume(TrySub(m_dirty_count, current.second.IsDirty()));
         // If we are not going to erase the cache, we must still erase spent entries.
         // Otherwise, clear the state of the entry.
         if (!m_will_erase) {
```

### src/util/overflow.h
```diff
@@ -31,6 +31,14 @@ template <class T>
     return i + j;
 }
 
+template <std::unsigned_integral T, std::unsigned_integral U>
+[[nodiscard]] constexpr bool TrySub(T& i, const U j) noexcept
+{
+    if (i < T{j}) return false;
+    i -= T{j};
+    return true;
+}
+
 template <class T>
 [[nodiscard]] T SaturatingAdd(const T i, const T j) noexcept
 {
```
