# [?] Fix expmod padding crash

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2026-01-12
Source: https://github.com/category-labs/monad/commit/cbbd825b4a5202143bbd06c471ade93015cb55dc
Type: security-commit

## Details
Fix expmod padding crash

## Patch
### category/execution/ethereum/precompiles_impl.cpp
```diff
@@ -258,11 +258,15 @@ constexpr uint64_t expmod_min_gas()
 
 // TODO(LH): Replace calls to this function with uint256_t::load_be_unsafe when
 // migrating off intx.
-static uint256_t uint256_partial_load_be(uint8_t const *bytes, size_t len)
+static uint256_t
+uint256_load_partial_be(byte_string_view const input, size_t const len)
 {
-    uint256_t result;
+    uint256_t result{};
     MONAD_VM_ASSERT(32 >= len);
-    std::memcpy(intx::as_bytes(result) + (32 - len), bytes, len);
+    std::memcpy(
+        intx::as_bytes(result) + (32 - len),
+        input.data(),
+        std::min(len, input.size()));
     return intx::to_big_endian(result);
 }
 
@@ -271,18 +275,13 @@ std::optional<uint64_t> expmod_gas_cost(byte_string_view const input)
 {
     static constexpr auto min_gas{expmod_min_gas<traits>()};
 
-    auto const base_len256 = uint256_partial_load_be(
-        &input.data()[0], std::min(32ul, input.length()));
-    auto const exp_len256 =
-        input.length() >= 32
-            ? uint256_partial_load_be(
-                  &input.data()[32], std::min(32ul, input.length() - 32))
-            : uint256_t{0};
-    auto const mod_len256 =
-        input.length() >= 64
-            ? uint256_partial_load_be(
-                  &input.data()[64], std::min(32ul, input.length() - 64))
-            : uint256_t{0};
+    auto const base_len256 = uint256_load_partial_be(input, 32);
+    auto const exp_len256 = input.length() >= 32
+                                ? uint256_load_partial_be(input.substr(32), 32)
+                                : uint256_t{0};
+    auto const mod_len256 = input.length() >= 64
+                                ? uint256_load_partial_be(input.substr(64), 32)
+                                : uint256_t{0};
 
     // Before EIP-7883, we could shortcut when the base and modulus lengths are
     // both zero. The EIP changes this to assume that both are at least 32 bytes
@@ -314,11 +313,8 @@ std::optional<uint64_t> expmod_gas_cost(byte_string_view const input)
     uint256_t exp_head{0}; // first 32 bytes of the exponent
     auto const exp_index = 96 + base_len64;
     if (input.length() > exp_index) { // input contains bytes of exponents
-        auto const exp_input_len =
-            std::min(exp_len64, input.length() - exp_index);
-        exp_head = uint256_partial_load_be(
-            &input.data()[exp_index],
-            std::min(32ul, static_cast<size_t>(exp_input_len)));
+        exp_head = uint256_load_partial_be(
+            input.substr(exp_index), std::min(32ul, exp_len64));
     }
     size_t const bit_len{256 - clz(exp_head)};
 
```

### category/execution/ethereum/precompiles_test.cpp
```diff
@@ -669,3 +669,81 @@ TYPED_TEST(TraitsTest, p256_verify)
             "p256_verify", "p256Verify.json", 0x0100_address);
     }
 }
+
+TYPED_TEST(TraitsTest, modexp_truncated_input)
+{
+    if constexpr (TestFixture::Trait::evm_rev() < EVMC_BYZANTIUM) {
+        GTEST_SKIP()
+            << "Modular Exponentiation precompile not available before "
+               "EVM Byzantium.";
+    }
+    else {
+        // Before Osaka, inputs to modexp could be arbitrarily large, and
+        // would just fail for gas reasons. After Osaka, the large padded
+        // modulus size in this example fails to validate.
+        static constexpr auto expected_failure =
+            TestFixture::Trait::eip_7823_active()
+                ? evmc_status_code::EVMC_FAILURE
+                : evmc_status_code::EVMC_OUT_OF_GAS;
+
+        static constexpr auto min_gas = [] {
+            if constexpr (TestFixture::Trait::evm_rev() >= EVMC_OSAKA) {
+                return 500;
+            }
+            else if constexpr (TestFixture::Trait::evm_rev() >= EVMC_BERLIN) {
+                return 200;
+            }
+            else {
+                return 10;
+            }
+        }();
+
+        auto const test_cases = std::array{
+            test_case{
+                .name = "truncated_modulus_len",
+                .input = evmc::from_hex(
+                             "0x00000000000000000000000000000000000000000000000"
+                             "0000000000000000100000000000000000000000000000000"
+                             "0000000000000000000000000000000100000000000000000"
+                             "000000000000000000000000000000005")
+                             .value(),
+                .expected_failure = expected_failure,
+                .gas = 30'000'000,
+            },
+            test_case{
+                .name = "truncated_exponent_len",
+                .input =
+                    evmc::from_hex("0x00000000000000000000000000000000000000000"
+                                   "0000000000000000000000100000000000000000000"
+                                   "00000000000000000000000000000005")
+                        .value(),
+                .expected_failure = expected_failure,
+                .gas = 30'000'000,
+            },
+            test_case{
+                .name = "truncated_base_len",
+                .input = evmc::from_hex("0x000000000000000000000000000000000000"
+                                        "00000000000000000500")
+                             .value(),
+                .expected_failure = expected_failure,
+                .gas = 30'000'000,
+            },
+            test_case{
+                .name = "truncated_exponent",
+                .input = evmc::from_hex("0x00000000000000000000000000000000000"
+                                        "000000000000000000000"
+                                        "0000000100000000000000000000000000000"
+                                        "000000000000000000000"
+                                        "0000000000000200000000000000000000000"
+                                        "000000000000000000000"
+                                        "000000000000000000050201")
+                             .value(),
+                .expected = evmc::from_hex("0x0000000000").value(),
+                .gas = min_gas,
+            },
+        };
+
+        do_geth_tests<typename TestFixture::Trait>(
+            "modexp_truncated_input", test_cases, 0x05_address);
+    }
+}
```
