# [?] :recycle: Fix possible overflow

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2023-10-12
Source: https://github.com/category-labs/monad/commit/6a15b8c95a589fd746ea70806e26440df8caca1b
Type: security-commit

## Details
:recycle: Fix possible overflow

## Patch
### include/monad/execution/ethereum/fork_traits.hpp
```diff
@@ -5,6 +5,7 @@
 #include <monad/core/assert.h>
 #include <monad/core/byte_string.hpp>
 #include <monad/core/bytes.hpp>
+#include <monad/core/int.hpp>
 #include <monad/core/likely.h>
 #include <monad/core/transaction.hpp>
 
@@ -45,6 +46,10 @@ namespace fork_traits
         Block const &b, uint256_t const &reward, uint256_t const &ommer_reward,
         uint256_t const &gas_award)
     {
+        MONAD_DEBUG_ASSERT(
+            reward + intx::umul(ommer_reward, uint256_t{b.ommers.size()}) +
+                gas_award <=
+            std::numeric_limits<uint256_t>::max());
         return reward + ommer_reward * b.ommers.size() + gas_award;
     }
 
```

### include/monad/execution/transaction_processor.hpp
```diff
@@ -3,6 +3,7 @@
 #include <monad/core/account.hpp>
 #include <monad/core/assert.h>
 #include <monad/core/block.hpp>
+#include <monad/core/int.hpp>
 #include <monad/core/receipt.hpp>
 #include <monad/core/transaction.hpp>
 
@@ -140,7 +141,8 @@ struct TransactionProcessor
         // v0 <= σ[S(T)]b
         else if (MONAD_UNLIKELY(
                      intx::be::load<uint256_t>(state.get_balance(*t.from)) <
-                     (t.value + t.gas_limit * t.max_fee_per_gas))) {
+                     (t.value +
+                      intx::umul(uint256_t(t.gas_limit), t.max_fee_per_gas)))) {
             return TransactionStatus::INSUFFICIENT_BALANCE;
         }
         // Note: Tg <= B_Hl - l(B_R)u can only be checked before retirement
```

### src/monad/execution/test/validation.cpp
```diff
@@ -190,3 +190,27 @@ TEST(Execution, priority_fee_greater_than_max)
     auto status = p.static_validate(t, 29'000'000'000);
     EXPECT_EQ(status, TransactionStatus::PRIORITY_FEE_GREATER_THAN_MAX);
 }
+
+TEST(Execution, insufficent_balance_overflow)
+{
+    static constexpr auto a{0xf8636377b7a998b51a3cf2bd711b870b3ab0ad56_address};
+    static constexpr auto b{0x5353535353535353535353535353535353535353_address};
+
+    db_t db;
+    block_cache_t block_cache;
+    BlockState<mutex_t> bs;
+    state_t s{bs, db, block_cache};
+    s.add_to_balance(a, std::numeric_limits<uint256_t>::max());
+
+    static Transaction const t{
+        .max_fee_per_gas = std::numeric_limits<uint256_t>::max() - 1,
+        .gas_limit = 1000,
+        .value = 0,
+        .to = b,
+        .from = a};
+
+    processor_t p{};
+
+    auto status = p.validate(s, t);
+    EXPECT_EQ(status, TransactionStatus::INSUFFICIENT_BALANCE);
+}
```
