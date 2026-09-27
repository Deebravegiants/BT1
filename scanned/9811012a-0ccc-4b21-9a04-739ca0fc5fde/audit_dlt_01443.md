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
