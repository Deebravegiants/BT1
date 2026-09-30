# [?] Merge bitcoin/bitcoin#35616: refactor: Use u64 over size_t for all cache sizes to fix a 32-bit overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-07-09
Source: https://github.com/bitcoin/bitcoin/commit/5223cf17954955ac7cb7d774d77f7aae271b610b
Type: security-commit

## Details
Merge bitcoin/bitcoin#35616: refactor: Use u64 over size_t for all cache sizes to fix a 32-bit overflow

fabafd91f173ea0d870816a49b81d074d5b8dbe2 refactor: Use u64 over size_t for all cache sizes to fix a 32-bit overflow (MarcoFalke)

Pull request description:

  This is a refactor on 64-bit systems, because size_t is equal to u64.

  However, on 32-bit systems, it fixes an integer overflow while calculating the cache sizes:

  ```
  src/node/caches.cpp:71:49: runtime error: unsigned integer overflow: 471859200 * 10 cannot be represented in type size_t (aka "unsigned int")
  ```

  This happens while multiplying the default cache size (450MiB) by 10:

  ```
  index_sizes.tx_index = std::min(total_cache * 10 / 100, ...)
                                  ^^^^^^^^^^^^^^^^
  ```

  The issue was introduced in commit d06dabf26bea7d9ca8d635e8338f64aec74c56a8.

  ----

  This change follows similar changed one in the past, like 3789215f73466606eb111714f596a2a5e9bb1933, ac76d94117be70d2dcc23ba34b120b44aeb3b0c1, or 28a523fb94d333fd8a28ca101cce746157a90fb6.

  Generally, using fixed sized integer types for calculations is beneficial, because all platforms behave exactly the same way. With platform-dependent types there is a risk that the same calculation yields different results. This has several resulting benefits:

  * Easier review, because there is no need to review the same code several times for each supported platform.
  * Easier quality assurance, because there is less need to run the same code several times in sanitizers for each supported platform, which is [tedious](https://github.com/bitcoin/bitcoin/issues/32375#issuecomment-4825318068).

  There are also no downsides, because there is no measurable overhead on 32-bit for u64 calculations that are done only once in the lifetime of the program. Also, there is no measurable memory overhead when a few fields on 32-bit store some extra zero bytes.

  ----

  As said, testing is only possible by picking one of the tedious options:

  * Apply a diff on 64-bit arch and compile with `-DCMAKE_C_COMPILER='clang' -DCMAKE_CXX_COMPILER='clang++'   -DSANITIZERS=integer`

  ```diff
  diff --git a/src/node/caches.cpp b/src/node/caches.cpp
  index c98b8ce604..cfd49b60d3 100644
  --- a/src/node/caches.cpp
  +++ b/src/node/caches.cpp
  @@ -58,3 +58,3 @@ CacheSizes CalculateCacheSizes(const ArgsManager& args, size_t n_indexes)
   {
  -    size_t total_cache{CalculateDbCacheBytes(args)};
  +    uint32_t total_cache(CalculateDbCacheBytes(args));

  @@ -72,6 +72,6 @@ CacheSizes CalculateCacheSizes(const ArgsManager& args, size_t n_indexes)
       IndexCacheSizes index_sizes;
  -    index_sizes.tx_index = std::min(total_cache * 10 / 100, args.GetBoolArg("-txindex", DEFAULT_TXINDEX) ? MAX_TX_INDEX_CACHE : 0);
  -    index_sizes.txospender_index = std::min(total_cache * 5 / 100, args.GetBoolArg("-txospenderindex", DEFAULT_TXOSPENDERINDEX) ? MAX_TXOSPENDER_INDEX_CACHE : 0);
  +    index_sizes.tx_index = std::min<uint32_t>(total_cache * 10 / 100, args.GetBoolArg("-txindex", DEFAULT_TXINDEX) ? MAX_TX_INDEX_CACHE : 0);
  +    index_sizes.txospender_index = std::min<uint32_t>(total_cache * 5 / 100, args.GetBoolArg("-txospenderindex", DEFAULT_TXOSPENDERINDEX) ? MAX_TXOSPENDER_INDEX_CACHE : 0);
       if (n_indexes > 0) {
  -        size_t max_cache = std::min(total_cache * 5 / 100, MAX_FILTER_INDEX_CACHE);
  +        size_t max_cache = std::min<uint32_t>(total_cache * 5 / 100, MAX_FILTER_INDEX_CACHE);
           index_sizes.filter_index = max_cache / n_indexes;
  ```

  This will give a roughly similar error:

  ```
  sh-5.3$ echo 'Bw==' | base64 -d > /tmp/blob
  sh-5.3$ UBSAN_OPTIONS="suppressions=$(pwd)/test/sanitizer_suppressions/ubsan:print_stacktrace=1:halt_on_error=1:report_error_type=1" FUZZ=block_index_tree ./bld-cmake/bin/fuzz /tmp/blob
  ./src/node/caches.cpp:73:59: runtime error: unsigned integer overflow: 1073741824 * 10 cannot be represented in type 'uint32_t' (aka 'unsigned int')
      #0 0x55ca78da5c47 in node::CalculateCacheSizes(ArgsManager const&, unsigned long) ./src/node/caches.cpp:73:59
  ```

  * Alternatively, to reproduce in a fresh `podman run -it --rm --platform linux/i386 debian:unstable`:

  ```
  export DEBIAN_FRONTEND=noninteractive && apt update && apt install curl wget htop git vim ccache -y && git clone https://github.com/bitcoin/bitcoin.git   ./b-c && cd b-c && apt install  build-essential cmake pkg-config  python3-zmq libzmq3-dev libevent-dev libboost-dev libsqlite3-dev  systemtap-sdt-dev  libcapnp-dev capnproto  libqrencode-dev qt6-tools-dev qt6-l10n-tools qt6-base-dev  clang llvm libc++-dev libc++abi-dev  mold -y   &&  cmake -B ./bld-cmake -DAPPEND_CXXFLAGS='-O3 -g2' -DAPPEND_CFLAGS='-O3 -g2' -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXE_LINKER_FLAGS=-fuse-ld=mold -DCMAKE_C_COMPILER='clang;-ftrivial-auto-var-init=pattern' -DCMAKE_CXX_COMPILER='clang++;-ftrivial-auto-var-init=pattern' -DSANITIZERS=address,float-divide-by-zero,integer,undefined --preset=dev-mode                              && cmake --build ./bld-cmake --parallel  $(nproc)

  echo 'Bw==' | base64 -d > /tmp/blob

  UBSAN_OPTIONS="suppressions=$(pwd)/test/sanitizer_suppressions/ubsan:print_stacktrace=1:halt_on_error=1:report_error_type=1" FUZZ=block_index_tree ./bld-cmake/bin/fuzz /tmp/blob

  # or:

  UBSAN_OPTIONS="suppressions=$(pwd)/test/sanitizer_suppressions/ubsan:print_stacktrace=1:halt_on_error=1:report_error_type=1" ASAN_OPTIONS="detect_leaks=0"  ./bld-cmake/bin/test_bitcoin-qt

  ```

ACKs for top commit:
  l0rinc:
    ACK fabafd91f173ea0d870816a49b81d074d5b8dbe2
  sedited:
    Re-ACK fabafd91f173ea0d870816a49b81d074d5b8dbe2
  theStack:
    re-ACK fabafd91f173ea0d870816a49b81d074d5b8dbe2

Tree-SHA512: cebbc29636b4074917c96cf3af8fcc176dcd328821d5032dc8609475e18778dfda4e287ded889c024ab29b79d81004bc9a8e57a88eaa0a5eaefe5f8bba1462ab

### src/dbwrapper.h
```diff
@@ -12,11 +12,14 @@
 #include <util/byte_units.h>
 #include <util/check.h>
 #include <util/fs.h>
+#include <util/obfuscation.h>
 
 #include <cstddef>
+#include <cstdint>
 #include <exception>
 #include <memory>
 #include <optional>
+#include <span>
 #include <stdexcept>
 #include <string>
 
@@ -39,7 +42,7 @@ struct DBParams {
     //! Location in the filesystem where leveldb data will be stored.
     fs::path path;
     //! Configures various leveldb cache settings.
-    size_t cache_bytes;
+    uint64_t cache_bytes;
     //! If true, use leveldb's memory environment.
     bool memory_only = false;
     //! If true, remove all existing data.
```

### src/kernel/caches.h
```diff
@@ -8,24 +8,25 @@
 #include <util/byte_units.h>
 
 #include <algorithm>
+#include <cstdint>
 
 //! Suggested default amount of cache reserved for the kernel (bytes)
-static constexpr size_t DEFAULT_KERNEL_CACHE{450_MiB};
+static constexpr uint64_t DEFAULT_KERNEL_CACHE{450_MiB};
 //! Default LevelDB write batch size
-static constexpr size_t DEFAULT_DB_CACHE_BATCH{32_MiB};
+static constexpr uint64_t DEFAULT_DB_CACHE_BATCH{32_MiB};
 
 //! Max memory allocated to block tree DB specific cache (bytes)
-static constexpr size_t MAX_BLOCK_DB_CACHE{2_MiB};
+static constexpr uint64_t MAX_BLOCK_DB_CACHE{2_MiB};
 //! Max memory allocated to coin DB specific cache (bytes)
-static constexpr size_t MAX_COINS_DB_CACHE{8_MiB};
+static constexpr uint64_t MAX_COINS_DB_CACHE{8_MiB};
 
 namespace kernel {
 struct CacheSizes {
-    size_t block_tree_db;
-    size_t coins_db;
-    size_t coins;
+    uint64_t block_tree_db;
+    uint64_t coins_db;
+    uint64_t coins;
 
-    CacheSizes(size_t total_cache)
+    CacheSizes(uint64_t total_cache)
     {
         block_tree_db = std::min(total_cache / 8, MAX_BLOCK_DB_CACHE);
         total_cache -= block_tree_db;
```

### src/node/caches.cpp
```diff
@@ -13,27 +13,31 @@
 #include <tinyformat.h>
 #include <util/byte_units.h>
 #include <util/log.h>
+#include <util/overflow.h>
+#include <util/translation.h>
 
 #include <algorithm>
+#include <cstdint>
+#include <limits>
 #include <string>
 
 // Unlike for the UTXO database, for the txindex scenario the leveldb cache make
 // a meaningful difference: https://github.com/bitcoin/bitcoin/pull/8273#issuecomment-229601991
 //! Max memory allocated to tx index DB specific cache in bytes.
-static constexpr size_t MAX_TX_INDEX_CACHE{1_GiB};
+static constexpr uint64_t MAX_TX_INDEX_CACHE{1_GiB};
 //! Max memory allocated to all block filter index caches combined in bytes.
-static constexpr size_t MAX_FILTER_INDEX_CACHE{1_GiB};
+static constexpr uint64_t MAX_FILTER_INDEX_CACHE{1_GiB};
 //! Max memory allocated to tx spenderindex DB specific cache in bytes.
-static constexpr size_t MAX_TXOSPENDER_INDEX_CACHE{1_GiB};
+static constexpr uint64_t MAX_TXOSPENDER_INDEX_CACHE{1_GiB};
 //! Maximum dbcache size on 32-bit systems.
-static constexpr size_t MAX_32BIT_DBCACHE{1_GiB};
+static constexpr uint64_t MAX_32BIT_DBCACHE{1_GiB};
 //! Larger default dbcache on 64-bit systems with enough RAM.
-static constexpr size_t HIGH_DEFAULT_DBCACHE{1_GiB};
+static constexpr uint64_t HIGH_DEFAULT_DBCACHE{1_GiB};
 //! Minimum detected RAM required for HIGH_DEFAULT_DBCACHE.
 static constexpr uint64_t HIGH_DEFAULT_DBCACHE_MIN_TOTAL_RAM{4_GiB};
 
 namespace node {
-size_t GetDefaultDBCache()
+uint64_t GetDefaultDBCache()
 {
     if constexpr (sizeof(void*) >= 8) {
         if (GetTotalRAM().value_or(0) >= HIGH_DEFAULT_DBCACHE_MIN_TOTAL_RAM) {
@@ -43,20 +47,20 @@ size_t GetDefaultDBCache()
     return DEFAULT_DB_CACHE;
 }
 
-size_t CalculateDbCacheBytes(const ArgsManager& args)
+uint64_t CalculateDbCacheBytes(const ArgsManager& args)
 {
     if (auto db_cache{args.GetIntArg("-dbcache")}) {
         if (*db_cache < 0) db_cache = 0;
         const uint64_t db_cache_bytes{SaturatingLeftShift<uint64_t>(*db_cache, 20)};
-        constexpr auto max_db_cache{sizeof(void*) == 4 ? MAX_32BIT_DBCACHE : std::numeric_limits<size_t>::max()};
-        return std::max<size_t>(MIN_DB_CACHE, std::min<uint64_t>(db_cache_bytes, max_db_cache));
+        constexpr uint64_t max_db_cache{sizeof(void*) == 4 ? MAX_32BIT_DBCACHE : std::numeric_limits<uint64_t>::max()};
+        return std::max<uint64_t>(MIN_DB_CACHE, std::min<uint64_t>(db_cache_bytes, max_db_cache));
     }
     return GetDefaultDBCache();
 }
 
 CacheSizes CalculateCacheSizes(const ArgsManager& args, size_t n_indexes)
 {
-    size_t total_cache{CalculateDbCacheBytes(args)};
+    uint64_t total_cache{CalculateDbCacheBytes(args)};
 
     // Allocate proportional to usage pattern benefit:
     // - txindex (10%): serves getrawtransaction RPCs with mostly unique,
@@ -73,7 +77,7 @@ CacheSizes CalculateCacheSizes(const ArgsManager& args, size_t n_indexes)
     index_sizes.tx_index = std::min(total_cache * 10 / 100, args.GetBoolArg("-txindex", DEFAULT_TXINDEX) ? MAX_TX_INDEX_CACHE : 0);
     index_sizes.txospender_index = std::min(total_cache * 5 / 100, args.GetBoolArg("-txospenderindex", DEFAULT_TXOSPENDERINDEX) ? MAX_TXOSPENDER_INDEX_CACHE : 0);
     if (n_indexes > 0) {
-        size_t max_cache = std::min(total_cache * 5 / 100, MAX_FILTER_INDEX_CACHE);
+        uint64_t max_cache = std::min(total_cache * 5 / 100, MAX_FILTER_INDEX_CACHE);
         index_sizes.filter_index = max_cache / n_indexes;
         total_cache -= index_sizes.filter_index * n_indexes;
     }
@@ -85,7 +89,7 @@ CacheSizes CalculateCacheSizes(const ArgsManager& args, size_t n_indexes)
 void LogOversizedDbCache(const ArgsManager& args) noexcept
 {
     if (const auto total_ram{GetTotalRAM()}) {
-        const size_t db_cache{CalculateDbCacheBytes(args)};
+        const uint64_t db_cache{CalculateDbCacheBytes(args)};
         if (ShouldWarnOversizedDbCache(db_cache, *total_ram)) {
             InitWarning(bilingual_str{tfm::format(_("A %zu MiB dbcache may be too large for a system memory of only %zu MiB."),
                         db_cache >> 20, *total_ram >> 20)});
```

### src/node/caches.h
```diff
@@ -9,20 +9,21 @@
 #include <util/byte_units.h>
 
 #include <cstddef>
+#include <cstdint>
 
 class ArgsManager;
 
 //! min. -dbcache (bytes)
-static constexpr size_t MIN_DB_CACHE{4_MiB};
+static constexpr uint64_t MIN_DB_CACHE{4_MiB};
 //! -dbcache default (bytes)
-static constexpr size_t DEFAULT_DB_CACHE{DEFAULT_KERNEL_CACHE};
+static constexpr uint64_t DEFAULT_DB_CACHE{DEFAULT_KERNEL_CACHE};
 
 namespace node {
-size_t GetDefaultDBCache();
+uint64_t GetDefaultDBCache();
 struct IndexCacheSizes {
-    size_t tx_index{0};
-    size_t filter_index{0};
-    size_t txospender_index{0};
+    uint64_t tx_index{0};
+    uint64_t filter_index{0};
+    uint64_t txospender_index{0};
 };
 struct CacheSizes {
     IndexCacheSizes index;
```

### src/txdb.h
```diff
@@ -27,7 +27,7 @@ class uint256;
 //! User-controlled performance and debug options.
 struct CoinsViewOptions {
     //! Maximum database write batch size in bytes.
-    size_t batch_write_bytes{DEFAULT_DB_CACHE_BATCH};
+    uint64_t batch_write_bytes{DEFAULT_DB_CACHE_BATCH};
     //! If non-zero, randomly exit when the database is flushed with (1/ratio) probability.
     int simulate_crash_ratio{0};
 };
```
