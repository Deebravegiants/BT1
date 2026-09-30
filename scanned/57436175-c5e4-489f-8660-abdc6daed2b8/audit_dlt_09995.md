# [?] Stub out EIP-4844 to prevent null deref

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2025-06-06
Source: https://github.com/category-labs/monad/commit/603a17a89c6d996ce49008f5cfa2654a5ac8b111
Type: security-commit

## Details
Stub out EIP-4844 to prevent null deref

## Patch
### libs/execution/src/monad/execution/precompiles.cpp
```diff
@@ -36,9 +36,9 @@ consteval unsigned num_precompiles(evmc_revision const rev)
     case EVMC_LONDON:
     case EVMC_PARIS:
     case EVMC_SHANGHAI:
-    case EVMC_CANCUN: // TODO(kkuehler): change to 10 after
-                      // https://github.com/monad-crypto/monad/pull/887
         return 9;
+    case EVMC_CANCUN:
+        return 10;
     case EVMC_PRAGUE:
         return 17;
     default:
@@ -83,8 +83,7 @@ inline constexpr std::array<
         {ecmul_gas_cost, ecmul_execute},
         {snarkv_gas_cost, snarkv_execute},
         {blake2bf_gas_cost, blake2bf_execute},
-        {nullptr, nullptr}, // TODO:
-                            // https://github.com/category-labs/monad/pull/968
+        {point_evaluation_gas_cost, point_evaluation_execute},
         {bls12_g1_add_gas_cost, bls12_g1_add_execute},
         {bls12_g1_msm_gas_cost, bls12_g1_msm_execute},
         {bls12_g2_add_gas_cost, bls12_g2_add_execute},
```

### libs/execution/src/monad/execution/precompiles.hpp
```diff
@@ -30,7 +30,7 @@ uint64_t ecadd_gas_cost(byte_string_view, evmc_revision);
 uint64_t ecmul_gas_cost(byte_string_view, evmc_revision);
 uint64_t snarkv_gas_cost(byte_string_view, evmc_revision);
 uint64_t blake2bf_gas_cost(byte_string_view, evmc_revision);
-// TODO: https://github.com/category-labs/monad/pull/968
+uint64_t point_evaluation_gas_cost(byte_string_view, evmc_revision);
 uint64_t bls12_g1_add_gas_cost(byte_string_view, evmc_revision);
 uint64_t bls12_g1_msm_gas_cost(byte_string_view, evmc_revision);
 uint64_t bls12_g2_add_gas_cost(byte_string_view, evmc_revision);
@@ -66,7 +66,7 @@ PrecompileResult ecadd_execute(byte_string_view);
 PrecompileResult ecmul_execute(byte_string_view);
 PrecompileResult snarkv_execute(byte_string_view);
 PrecompileResult blake2bf_execute(byte_string_view);
-// TODO: https://github.com/category-labs/monad/pull/968
+PrecompileResult point_evaluation_execute(byte_string_view);
 PrecompileResult bls12_g1_add_execute(byte_string_view);
 PrecompileResult bls12_g1_msm_execute(byte_string_view);
 PrecompileResult bls12_g2_add_execute(byte_string_view);
```

### libs/execution/src/monad/execution/precompiles_impl.cpp
```diff
@@ -88,6 +88,12 @@ uint64_t expmod_gas_cost(byte_string_view const input, evmc_revision const rev)
         input.data(), input.size(), static_cast<int>(rev));
 }
 
+uint64_t point_evaluation_gas_cost(byte_string_view, evmc_revision)
+{
+    // TODO: https://github.com/category-labs/monad/pull/968
+    return 50'000;
+}
+
 uint64_t bls12_g1_add_gas_cost(byte_string_view, evmc_revision)
 {
     return 375;
@@ -196,6 +202,12 @@ PrecompileResult blake2bf_execute(byte_string_view const input)
     return silkpre_execute<silkpre_blake2_f_run>(input);
 }
 
+PrecompileResult point_evaluation_execute(byte_string_view)
+{
+    // TODO: https://github.com/category-labs/monad/pull/968
+    return PrecompileResult::failure();
+}
+
 PrecompileResult bls12_g1_add_execute(byte_string_view const input)
 {
     return bls12::add<bls12::G1>(input);
```
