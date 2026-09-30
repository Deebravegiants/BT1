# [?] Add suppressions for Rijndael::Base::FillEncTable and Rijndael::Base::FillDecTable. There is a race condition when initializing these tables but since

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-11-19
Source: https://github.com/nanocurrency/nano-node/commit/5d369ddcdd6c9c668f1d6703066c34728e15643c
Type: security-commit

## Details
Add suppressions for Rijndael::Base::FillEncTable and Rijndael::Base::FillDecTable. There is a race condition when initializing these tables but since their contents is static, the fields will always have the correct, constant values.

## Patch
### nano/core_test/uint256_union.cpp
```diff
@@ -1,8 +1,11 @@
+#include <nano/crypto_lib/random_pool.hpp>
 #include <nano/secure/common.hpp>
 #include <nano/test_common/testutil.hpp>
 
 #include <gtest/gtest.h>
 
+#include <thread>
+
 namespace
 {
 template <typename Union, typename Bound>
@@ -567,3 +570,19 @@ void check_operator_greater_than (Num lhs, Num rhs)
 	ASSERT_FALSE (rhs > rhs);
 }
 }
+
+TEST (random_pool, multithreading)
+{
+	std::vector<std::thread> threads;
+	for (auto i = 0; i < 100; ++i)
+	{
+		threads.emplace_back ([] () {
+			nano::uint256_union number;
+			nano::random_pool::generate_block (number.bytes.data (), number.bytes.size ());
+		});
+	}
+	for (auto & i : threads)
+	{
+		i.join ();
+	}
+}
```

### tsan_suppressions
```diff
@@ -1,2 +1,4 @@
 race:mdb.c
 race:rocksdb
+race:Rijndael::Base::FillEncTable
+race:Rijndael::Base::FillDecTable
```
