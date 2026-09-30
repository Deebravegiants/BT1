# [?] Patch RPC dos

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2025-11-20
Source: https://github.com/category-labs/monad/commit/dfd5207b9ae874861f24e051a43db885ac94a20a
Type: security-commit

## Details
Patch RPC dos

## Patch
### category/execution/monad/reserve_balance.cpp
```diff
@@ -15,6 +15,7 @@
 
 #include <category/core/assert.h>
 #include <category/core/config.hpp>
+#include <category/core/monad_exception.hpp>
 #include <category/execution/ethereum/core/transaction.hpp>
 #include <category/execution/ethereum/state3/state.hpp>
 #include <category/execution/ethereum/transaction_gas.hpp>
@@ -93,7 +94,9 @@ bool dipped_into_reserve(
             if (addr == sender) {
                 if (!can_sender_dip_into_reserve(
                         sender, i, effective_is_delegated, ctx)) {
-                    MONAD_ASSERT(
+                    // Safety: this assertion is recoverable because it can be
+                    // triggered via RPC parameter setting.
+                    MONAD_ASSERT_THROW(
                         violation_threshold.has_value(),
                         "gas fee greater than reserve for non-dipping "
                         "transaction");
@@ -102,6 +105,10 @@ bool dipped_into_reserve(
                 // Skip if allowed to dip into reserve
             }
             else {
+                // Safety: this assertion should not be a recoverable one, as it
+                // indicates a logic error in the surrounding code: the
+                // violation threshold can only be nullopt when addr == sender,
+                // which is not the case in this branch.
                 MONAD_ASSERT(violation_threshold.has_value());
                 return true;
             }
```

### category/rpc/monad_executor_test.cpp
```diff
@@ -3704,3 +3704,118 @@ TEST_F(EthCallFixture, eth_call_reserve_balance_emptying)
     monad_executor_destroy(executor);
     monad_state_override_destroy(state_override);
 }
+
+// Check that gas < reserve assertion in reserve balance implementation doesn't
+// crash the RPC process
+TEST_F(EthCallFixture, eth_call_reserve_balance_assertion)
+{
+    for (uint64_t i = 0; i < 256; ++i) {
+        commit_sequential(tdb, {}, {}, BlockHeader{.number = i});
+    }
+
+    static constexpr auto sender =
+        0x0000000000000000000000000000000011111111_address;
+
+    static constexpr auto contract =
+        0x0000000000000000000000000000000022222222_address;
+
+    static constexpr auto recipient =
+        0x0000000000000000000000000000000044444444_address;
+
+    // No-op delegation target
+    auto const contract_code = 0x00_bytes;
+    auto const contract_code_hash = to_bytes(keccak256(contract_code));
+    auto const contract_icode = monad::vm::make_shared_intercode(contract_code);
+
+    // Delegate to contract
+    auto const delegated_eoa_code =
+        0xef01000000000000000000000000000000000022222222_bytes;
+    auto const delegated_eoa_code_hash =
+        to_bytes(keccak256(delegated_eoa_code));
+    auto const delegated_eoa_icode =
+        monad::vm::make_shared_intercode(delegated_eoa_code);
+
+    EXPECT_TRUE(vm::evm::is_delegated(delegated_eoa_code));
+
+    BlockHeader const header{
+        .number = 256,
+        .base_fee_per_gas = 100'000'000'000,
+    };
+
+    commit_sequential(
+        tdb,
+        StateDeltas{
+            {sender,
+             StateDelta{
+                 .account =
+                     {std::nullopt,
+                      Account{
+                          .balance = uint256_t{1'000'000'000'000'000'000} * 12,
+                          .code_hash = delegated_eoa_code_hash,
+                          .nonce = 0}}}},
+            {contract,
+             StateDelta{
+                 .account =
+                     {std::nullopt,
+                      Account{
+                          .balance = 0,
+                          .code_hash = contract_code_hash,
+                          .nonce = 0}}}},
+            {recipient,
+             StateDelta{
+                 .account =
+                     {std::nullopt,
+                      Account{
+                          .balance = 0, .code_hash = NULL_HASH, .nonce = 0}}}},
+        },
+        Code{
+            {delegated_eoa_code_hash, delegated_eoa_icode},
+            {contract_code_hash, contract_icode},
+        },
+        header);
+
+    Transaction const tx{
+        .max_fee_per_gas = 100'000'000'000'001,
+        .gas_limit = 100'000u,
+        .to = recipient,
+    };
+
+    auto const rlp_tx = to_vec(rlp::encode_transaction(tx));
+    auto const rlp_header = to_vec(rlp::encode_block_header(header));
+    auto const rlp_sender =
+        to_vec(rlp::encode_address(std::make_optional(sender)));
+    auto const rlp_block_id = to_vec(rlp_finalized_id);
+
+    auto *executor = create_executor(dbname.string());
+    auto *state_override = monad_state_override_create();
+
+    struct callback_context ctx;
+    boost::fibers::future<void> f = ctx.promise.get_future();
+
+    monad_executor_eth_call_submit(
+        executor,
+        CHAIN_CONFIG_MONAD_DEVNET,
+        rlp_tx.data(),
+        rlp_tx.size(),
+        rlp_header.data(),
+        rlp_header.size(),
+        rlp_sender.data(),
+        rlp_sender.size(),
+        header.number,
+        rlp_block_id.data(),
+        rlp_block_id.size(),
+        state_override,
+        complete_callback,
+        (void *)&ctx,
+        NOOP_TRACER,
+        true);
+    f.get();
+
+    EXPECT_EQ(ctx.result->status_code, EVMC_INTERNAL_ERROR);
+    EXPECT_EQ(
+        std::string_view{ctx.result->message},
+        "gas fee greater than reserve for non-dipping transaction");
+
+    monad_executor_destroy(executor);
+    monad_state_override_destroy(state_override);
+}
```
