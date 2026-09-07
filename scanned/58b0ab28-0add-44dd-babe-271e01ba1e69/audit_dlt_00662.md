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


_Trimmed to 38 lines — full report: https://github.com/bitcoin/bitcoin/commit/5223cf17954955ac7cb7d774d77f7aae271b610b_
