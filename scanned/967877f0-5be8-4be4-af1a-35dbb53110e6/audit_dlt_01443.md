# [?] coins: fix `cachedCoinsUsage` accounting to prevent underflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-04-18
Source: https://github.com/bitcoin/bitcoin/commit/d7c9d6c2914aadd711544908d0fad8857a809c72
Type: security-commit

## Details
coins: fix `cachedCoinsUsage` accounting to prevent underflow

Move the `cachedCoinsUsage` subtract in `AddCoin()` to after the `possible_overwrite` check.
Previously a throw before assignment decremented the counter without changing the entry, which corrupted accounting and later underflowed.

In `Flush()`, reset `cachedCoinsUsage` to `0` only when `BatchWrite()` succeeds and `cacheCoins` is actually cleared. In production `BatchWrite()` returns `true`, so this mostly affects tests. On failure, leave the counter unchanged to keep it in sync with the cache.

The existing `Flush()` workaround in fuzzing was also removed now that the source of the problem was fixed, so the fuzzer no longer needs `coins_view_cache.Flush()` to realign `cachedCoinsUsage` after an exception.
Replace the prior `expected_code_path` tracking with direct assertions. The role of the variable was to verify that code execution follows only expected paths, either successful addition, or if it's an exception, the message is verified and checked that overwrite was disallowed.

With these changes the counter stays consistent across success and exception paths, so we can finally remove the `UBSan` suppressions for `CCoinsViewCache` that were masking the issue.

Included a unit test as well, attempting to add a different coin to the same outpoint without allowing overwrites and make sure it throws.
We use `SelfTest()` to validates accounting, and check that the cache remains usable.

Co-authored-by: Ryan Ofsky <ryan@ofsky.org>
Co-authored-by: w0xlt <woltx@protonmail.com>

## Patch
### src/coins.cpp
```diff
@@ -76,9 +76,6 @@ void CCoinsViewCache::AddCoin(const COutPoint &outpoint, Coin&& coin, bool possi
     bool inserted;
     std::tie(it, inserted) = cacheCoins.emplace(std::piecewise_construct, std::forward_as_tuple(outpoint), std::tuple<>());
     bool fresh = false;
-    if (!inserted) {
-        cachedCoinsUsage -= it->second.coin.DynamicMemoryUsage();
-    }
     if (!possible_overwrite) {
         if (!it->second.coin.IsSpent()) {
             throw std::logic_error("Attempted to overwrite an unspent coin (when possible_overwrite is false)");
@@ -98,6 +95,9 @@ void CCoinsViewCache::AddCoin(const COutPoint &outpoint, Coin&& coin, bool possi
         // DIRTY, then it can be marked FRESH.
         fresh = !it->second.IsDirty();
     }
+    if (!inserted) {
+        cachedCoinsUsage -= it->second.coin.DynamicMemoryUsage();
+    }
     it->second.coin = std::move(coin);
     CCoinsCacheEntry::SetDirty(*it, m_sentinel);
     if (fresh) CCoinsCacheEntry::SetFresh(*it, m_sentinel);
@@ -254,8 +254,8 @@ bool CCoinsViewCache::Flush() {
     if (fOk) {
         cacheCoins.clear();
         ReallocateCache();
+        cachedCoinsUsage = 0;
     }
-    cachedCoinsUsage = 0;
     return fOk;
 }
 
```

### src/test/coins_tests.cpp
```diff
@@ -1085,4 +1085,22 @@ BOOST_AUTO_TEST_CASE(coins_resource_is_used)
     PoolResourceTester::CheckAllDataAccountedFor(resource);
 }
 
+BOOST_AUTO_TEST_CASE(ccoins_addcoin_exception_keeps_usage_balanced)
+{
+    CCoinsView root;
+    CCoinsViewCacheTest cache{&root};
+
+    const COutPoint outpoint{Txid::FromUint256(m_rng.rand256()), m_rng.rand32()};
+
+    const Coin coin1{CTxOut{m_rng.randrange(10), CScript{} << m_rng.randbytes(CScriptBase::STATIC_SIZE + 1)}, 1, false};
+    cache.AddCoin(outpoint, Coin{coin1}, /*possible_overwrite=*/false);
+    cache.SelfTest();
+
+    const Coin coin2{CTxOut{m_rng.randrange(20), CScript{} << m_rng.randbytes(CScriptBase::STATIC_SIZE + 2)}, 2, false};
+    BOOST_CHECK_THROW(cache.AddCoin(outpoint, Coin{coin2}, /*possible_overwrite=*/false), std::logic_error);
+    cache.SelfTest();
+
+    BOOST_CHECK(cache.AccessCoin(outpoint) == coin1);
+}
+
 BOOST_AUTO_TEST_SUITE_END()
```

### src/test/fuzz/coins_view.cpp
```diff
@@ -59,25 +59,15 @@ void TestCoinsView(FuzzedDataProvider& fuzzed_data_provider, CCoinsView& backend
                 if (random_coin.IsSpent()) {
                     return;
                 }
-                Coin coin = random_coin;
-                bool expected_code_path = false;
-                const bool possible_overwrite = fuzzed_data_provider.ConsumeBool();
+                COutPoint outpoint{random_out_point};
+                Coin coin{random_coin};
+                const bool possible_overwrite{fuzzed_data_provider.ConsumeBool()};
                 try {
-                    coins_view_cache.AddCoin(random_out_point, std::move(coin), possible_overwrite);
-                    expected_code_path = true;
+                    coins_view_cache.AddCoin(outpoint, std::move(coin), possible_overwrite);
                 } catch (const std::logic_error& e) {
-                    if (e.what() == std::string{"Attempted to overwrite an unspent coin (when possible_overwrite is false)"}) {
-                        assert(!possible_overwrite);
-                        expected_code_path = true;
-                        // AddCoin() decreases cachedCoinsUsage by the memory usage of the old coin at the beginning and
-                        // increases it by the value of the new coin at the end. If it throws in the process, the value
-                        // of cachedCoinsUsage would have been incorrectly decreased, leading to an underflow later on.
-                        // To avoid this, use Flush() to reset the value of cachedCoinsUsage in sync with the cacheCoins
-                        // mapping.
-                        (void)coins_view_cache.Flush();
-                    }
+                    assert(e.what() == std::string{"Attempted to overwrite an unspent coin (when possible_overwrite is false)"});
+                    assert(!possible_overwrite);
                 }
-                assert(expected_code_path);
             },
             [&] {
                 (void)coins_view_cache.Flush();
```

### test/sanitizer_suppressions/ubsan
```diff
@@ -47,11 +47,6 @@ unsigned-integer-overflow:arith_uint256.h
 unsigned-integer-overflow:CBloomFilter::Hash
 unsigned-integer-overflow:CRollingBloomFilter::insert
 unsigned-integer-overflow:RollingBloomHash
-unsigned-integer-overflow:CCoinsViewCache::AddCoin
-unsigned-integer-overflow:CCoinsViewCache::BatchWrite
-unsigned-integer-overflow:CCoinsViewCache::DynamicMemoryUsage
-unsigned-integer-overflow:CCoinsViewCache::SpendCoin
-unsigned-integer-overflow:CCoinsViewCache::Uncache
 unsigned-integer-overflow:CompressAmount
 unsigned-integer-overflow:DecompressAmount
 unsigned-integer-overflow:crypto/
```
