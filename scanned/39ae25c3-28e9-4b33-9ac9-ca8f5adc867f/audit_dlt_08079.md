# [?] fuzz: avoid underflow in coins_view target

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2024-01-02
Source: https://github.com/bitcoin/bitcoin/commit/56d878c4650cc46ce54d1d79db054ac44b486605
Type: security-commit

## Details
fuzz: avoid underflow in coins_view target

## Patch
### src/test/fuzz/coins_view.cpp
```diff
@@ -69,6 +69,12 @@ FUZZ_TARGET(coins_view, .init = initialize_coins_view)
                     if (e.what() == std::string{"Attempted to overwrite an unspent coin (when possible_overwrite is false)"}) {
                         assert(!possible_overwrite);
                         expected_code_path = true;
+                        // AddCoin() decreases cachedCoinsUsage by the memory usage of the old coin at the beginning and
+                        // increases it by the value of the new coin at the end. If it throws in the process, the value
+                        // of cachedCoinsUsage would have been incorrectly decreased, leading to an underflow later on.
+                        // To avoid this, use Flush() to reset the value of cachedCoinsUsage in sync with the cacheCoins
+                        // mapping.
+                        (void)coins_view_cache.Flush();
                     }
                 }
                 assert(expected_code_path);
```
