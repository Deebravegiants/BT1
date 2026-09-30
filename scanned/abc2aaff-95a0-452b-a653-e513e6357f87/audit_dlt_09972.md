# [?] Prevent kernel fee overflow

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2026-03-28
Source: https://github.com/litecoin-project/litecoin/commit/42e7071a4263f146d1bb56717540be0343e7f23b
Type: security-commit

## Details
Prevent kernel fee overflow

## Patch
### src/consensus/tx_verify.cpp
```diff
@@ -236,10 +236,13 @@ bool Consensus::CheckTxInputs(const CTransaction& tx, TxValidationState& state,
             }
         }
 
-        CAmount mweb_fee = tx.mweb_tx.GetFee();
-        txfee_aux += mweb_fee;
+        const auto mweb_fee = tx.mweb_tx.GetFee();
+        if (!mweb_fee) {
+            return state.Invalid(TxValidationResult::TX_CONSENSUS, "bad-txns-mwebfee-outofrange");
+        }
 
-        if (!MoneyRange(mweb_fee) || !MoneyRange(txfee_aux)) {
+        txfee_aux += *mweb_fee;
+        if (!MoneyRange(*mweb_fee) || !MoneyRange(txfee_aux)) {
             return state.Invalid(TxValidationResult::TX_CONSENSUS, "bad-txns-mwebfee-outofrange");
         }
     }
```

### src/libmw/include/mw/consensus/Amount.h
```diff
@@ -0,0 +1,81 @@
+#pragma once
+
+#include <amount.h>
+#include <mw/exceptions/ValidationException.h>
+
+#include <boost/optional.hpp>
+#include <limits>
+
+namespace AmountUtil
+{
+inline bool IsValidMoney(const CAmount amount) noexcept
+{
+    return MoneyRange(amount);
+}
+
+inline bool IsValidAmountRange(const CAmount amount) noexcept
+{
+    return amount >= -MAX_MONEY && amount <= MAX_MONEY;
+}
+
+inline void ValidateMoney(const CAmount amount)
+{
+    if (!IsValidMoney(amount)) {
+        ThrowValidation(EConsensusError::AMOUNT_OUT_OF_RANGE);
+    }
+}
+
+inline void ValidateAmountRange(const CAmount amount)
+{
+    if (!IsValidAmountRange(amount)) {
+        ThrowValidation(EConsensusError::AMOUNT_OUT_OF_RANGE);
+    }
+}
+
+inline boost::optional<CAmount> TrySafeAdd(const CAmount lhs, const CAmount rhs) noexcept
+{
+    if ((rhs > 0 && lhs > std::numeric_limits<CAmount>::max() - rhs)
+        || (rhs < 0 && lhs < std::numeric_limits<CAmount>::min() - rhs))
+    {
+        return boost::none;
+    }
+
+    return lhs + rhs;
+}
+
+inline CAmount SafeAdd(const CAmount lhs, const CAmount rhs)
+{
+    const auto sum = TrySafeAdd(lhs, rhs);
+    if (!sum) {
+        ThrowValidation(EConsensusError::AMOUNT_OUT_OF_RANGE);
+    }
+
+    return *sum;
+}
+
+inline boost::optional<CAmount> TrySafeSubtract(const CAmount lhs, const CAmount rhs) noexcept
+{
+    if ((rhs > 0 && lhs < std::numeric_limits<CAmount>::min() + rhs)
+        || (rhs < 0 && lhs > std::numeric_limits<CAmount>::max() + rhs))
+    {
+        return boost::none;
+    }
+
+    return lhs - rhs;
+}
+
+inline CAmount SafeSubtract(const CAmount lhs, const CAmount rhs)
+{
+    const auto difference = TrySafeSubtract(lhs, rhs);
+    if (!difference) {
+        ThrowValidation(EConsensusError::AMOUNT_OUT_OF_RANGE);
+    }
+
+    return *difference;
+}
+
+inline uint64_t UnsignedAbs(const CAmount amount)
+{
+    return amount >= 0 ? static_cast<uint64_t>(amount) : static_cast<uint64_t>(-(amount + 1)) + 1;
+}
+} // namespace AmountUtil
```

### src/libmw/include/mw/consensus/KernelSumValidator.h
```diff
@@ -1,5 +1,6 @@
 #pragma once
 
+#include <mw/consensus/Amount.h>
 #include <mw/exceptions/ValidationException.h>
 #include <mw/crypto/Pedersen.h>
 #include <mw/models/tx/TxBody.h>
@@ -24,7 +25,13 @@ class KernelSumValidator
         // Sum all utxo commitments - expected supply.
         int64_t total_mweb_supply = 0;
         for (const Kernel& kernel : kernels) {
-            total_mweb_supply += kernel.GetSupplyChange();
+            const auto supply_change = kernel.GetSupplyChange();
+            if (!supply_change) {
+                ThrowValidation(EConsensusError::AMOUNT_OUT_OF_RANGE);
+            }
+
+            total_mweb_supply = AmountUtil::SafeAdd(total_mweb_supply, *supply_change);
+            AmountUtil::ValidateAmountRange(total_mweb_supply);
 
             // Total supply can never go below 0
             if (total_mweb_supply < 0) {
@@ -56,7 +63,7 @@ class KernelSumValidator
             body.GetOutputCommits(),
             body.GetKernelCommits(),
             block_offset,
-            body.GetSupplyChange()
+            GetAmountOrThrow(body.GetSupplyChange())
         );
     }
 
@@ -67,18 +74,29 @@ class KernelSumValidator
             tx.GetOutputCommits(),
             tx.GetKernelCommits(),
             tx.GetKernelOffset(),
-            tx.GetSupplyChange()
+            GetAmountOrThrow(tx.GetSupplyChange())
         );
     }
 
 private:
+    static CAmount GetAmountOrThrow(const boost::optional<CAmount>& amount)
+    {
+        if (!amount) {
+            ThrowValidation(EConsensusError::AMOUNT_OUT_OF_RANGE);
+        }
+
+        return *amount;
+    }
+
     static void ValidateSums(
         const std::vector<Commitment>& input_commits,
         const std::vector<Commitment>& output_commits,
         const std::vector<Commitment>& kernel_commits,
         const BlindingFactor& offset,
         const int64_t coins_added)
     {
+        AmountUtil::ValidateAmountRange(coins_added);
+
         // Calculate UTXO nonce sum
         Commitment sum_utxo_commitment = Pedersen::AddCommitments(output_commits, input_commits);
         if (coins_added > 0) {
@@ -87,7 +105,7 @@ class KernelSumValidator
             );
         } else if (coins_added < 0) {
             sum_utxo_commitment = Pedersen::AddCommitments(
-                { sum_utxo_commitment, Commitment::Transparent(std::abs(coins_added)) }
+                { sum_utxo_commitment, Commitment::Transparent(AmountUtil::UnsignedAbs(coins_added)) }
             );
         }
 
@@ -108,4 +126,4 @@ class KernelSumValidator
             ThrowValidation(EConsensusError::BLOCK_SUMS);
         }
     }
-};
\ No newline at end of file
+};
```

### src/libmw/include/mw/exceptions/ValidationException.h
```diff
@@ -11,6 +11,7 @@ enum class EConsensusError
     DUPLICATES,
     BLOCK_WEIGHT,
     BLOCK_SUMS,
+    AMOUNT_OUT_OF_RANGE,
     STEALTH_SUMS,
     INVALID_SIG,
     BULLETPROOF,
@@ -50,6 +51,8 @@ class ValidationException : public LTCException
                 return "BLOCK_WEIGHT";
             case EConsensusError::BLOCK_SUMS:
                 return "BLOCK_SUMS";
+            case EConsensusError::AMOUNT_OUT_OF_RANGE:
+                return "AMOUNT_OUT_OF_RANGE";
             case EConsensusError::STEALTH_SUMS:
                 return "STEALTH_SUMS";
             case EConsensusError::INVALID_SIG:
```

### src/libmw/include/mw/models/block/Block.h
```diff
@@ -50,11 +50,11 @@ class Block final :
     const BlindingFactor& GetKernelOffset() const noexcept { return m_pHeader->GetKernelOffset(); }
     const BlindingFactor& GetStealthOffset() const noexcept { return m_pHeader->GetStealthOffset(); }
 
-    CAmount GetTotalFee() const noexcept { return m_body.GetTotalFee(); }
+    boost::optional<CAmount> GetTotalFee() const noexcept { return m_body.GetTotalFee(); }
     std::vector<PegInCoin> GetPegIns() const noexcept { return m_body.GetPegIns(); }
-    CAmount GetPegInAmount() const noexcept { return m_body.GetPegInAmount(); }
+    boost::optional<CAmount> GetPegInAmount() const noexcept { return m_body.GetPegInAmount(); }
     std::vector<PegOutCoin> GetPegOuts() const noexcept { return m_body.GetPegOuts(); }
-    CAmount GetSupplyChange() const noexcept { return m_body.GetSupplyChange(); }
+    boost::optional<CAmount> GetSupplyChange() const noexcept { return m_body.GetSupplyChange(); }
 
     //
     // Serialization/Deserialization
@@ -126,4 +126,4 @@ class MutBlock
     std::vector<Kernel> m_kernels;
 };
 
-END_NAMESPACE
\ No newline at end of file
+END_NAMESPACE
```

### src/libmw/include/mw/models/tx/Kernel.h
```diff
@@ -2,6 +2,7 @@
 
 #include <mw/common/Macros.h>
 #include <mw/common/Traits.h>
+#include <mw/consensus/Amount.h>
 #include <mw/crypto/Hasher.h>
 #include <mw/models/crypto/BlindingFactor.h>
 #include <mw/models/crypto/Commitment.h>
@@ -105,17 +106,46 @@ class Kernel :
     CAmount GetPegIn() const noexcept { return m_pegin.value_or(0); }
     const std::vector<PegOutCoin>& GetPegOuts() const noexcept { return m_pegouts; }
 
-    CAmount GetPegOutAmount() const noexcept
+    boost::optional<CAmount> GetPegOutAmount() const noexcept
     {
-        return std::accumulate(
-            m_pegouts.cbegin(), m_pegouts.cend(), (CAmount)0,
-            [](CAmount sum, const PegOutCoin& pegout) { return sum + pegout.GetAmount(); }
-        );
+        CAmount total = 0;
+        for (const PegOutCoin& pegout : m_pegouts) {
+            if (!AmountUtil::IsValidMoney(pegout.GetAmount())) {
+                return boost::none;
+            }
+
+            const auto next_total = AmountUtil::TrySafeAdd(total, pegout.GetAmount());
+            if (!next_total || !AmountUtil::IsValidMoney(*next_total)) {
+                return boost::none;
+            }
+
+            total = *next_total;
+        }
+
+        return total;
     }
 
-    CAmount GetSupplyChange() const noexcept
+    boost::optional<CAmount> GetSupplyChange() const noexcept
     {
-        return (m_pegin.value_or(0) - m_fee.value_or(0)) - GetPegOutAmount();
+        const CAmount pegin = m_pegin.value_or(0);
+        const CAmount fee = m_fee.value_or(0);
+        const auto pegout_amount = GetPegOutAmount();
+
+        if (!AmountUtil::IsValidMoney(pegin) || !AmountUtil::IsValidMoney(fee) || !pegout_amount) {
+            return boost::none;
+        }
+
+        const auto supply_after_fee = AmountUtil::TrySafeSubtract(pegin, fee);
+        if (!supply_after_fee) {
+            return boost::none;
+        }
+
+        const auto supply_change = AmountUtil::TrySafeSubtract(*supply_after_fee, *pegout_amount);
+        if (!supply_change || !AmountUtil::IsValidAmountRange(*supply_change)) {
+            return boost::none;
+        }
+
+        return *supply_change;
     }
 
     //
@@ -221,8 +251,22 @@ static const struct
 {
     bool operator()(const Kernel& a, const Kernel& b) const
     {
-        CAmount a_pegin = a.GetSupplyChange();
-        CAmount b_pegin = b.GetSupplyChange();
-        return (a_pegin > b_pegin) || (a_pegin == b_pegin && a.GetHash() < b.GetHash());
+        const auto a_supply_change = a.GetSupplyChange();
+        const auto b_supply_change = b.GetSupplyChange();
+
+        if (a_supply_change && b_supply_change) {
+            return (*a_supply_change > *b_supply_change)
+                || (*a_supply_change == *b_supply_change && a.GetHash() < b.GetHash());
+        }
+
+        if (a_supply_change) {
+            return true;
+        }
+
+        if (b_supply_change) {
+            return false;
+        }
+
+        return a.GetHash() < b.GetHash();
     }
-} KernelSort;
\ No newline at end of file
+} KernelSort;
```

### src/libmw/include/mw/models/tx/Transaction.h
```diff
@@ -75,17 +75,17 @@ class Transaction :
     const std::vector<Input>& GetInputs() const noexcept { return m_body.GetInputs(); }
     const std::vector<Output>& GetOutputs() const noexcept { return m_body.GetOutputs(); }
     const std::vector<Kernel>& GetKernels() const noexcept { return m_body.GetKernels(); }
-    CAmount GetTotalFee() const noexcept { return m_body.GetTotalFee(); }
+    boost::optional<CAmount> GetTotalFee() const noexcept { return m_body.GetTotalFee(); }
     int32_t GetLockHeight() const noexcept { return m_body.GetLockHeight(); }
     uint64_t CalcWeight() const noexcept { return (uint64_t)Weight::Calculate(m_body); }
 
     std::vector<Commitment> GetKernelCommits() const noexcept { return m_body.GetKernelCommits(); }
     std::vector<Commitment> GetInputCommits() const noexcept { return m_body.GetInputCommits(); }
     std::vector<Commitment> GetOutputCommits() const noexcept { return m_body.GetOutputCommits(); }
     std::vector<PegInCoin> GetPegIns() const noexcept { return m_body.GetPegIns(); }
-    CAmount GetPegInAmount() const noexcept { return m_body.GetPegInAmount(); }
+    boost::optional<CAmount> GetPegInAmount() const noexcept { return m_body.GetPegInAmount(); }
     std::vector<PegOutCoin> GetPegOuts() const noexcept { return m_body.GetPegOuts(); }
-    CAmount GetSupplyChange() const noexcept { return m_body.GetSupplyChange(); }
+    boost::optional<CAmount> GetSupplyChange() const noexcept { return m_body.GetSupplyChange(); }
 
     //
     // Serialization/Deserialization
@@ -113,15 +113,16 @@ class Transaction :
     bool IsStandard() const noexcept;
     void Validate() const;
     
-    std::string Print() const noexcept
+    std::string Print() const
     {
         auto print_kernel = [](const Kernel& kernel) -> std::string {
+            const auto pegout_amount = kernel.GetPegOutAmount();
             return StringUtil::Format(
                 "kern(kernel_id:{}, commit:{}, pegin: {}, pegout: {}, fee: {})",
                 kernel.GetKernelID(),
                 kernel.GetCommitment(),
                 kernel.GetPegIn(),
-                kernel.GetPegOutAmount(),
+                pegout_amount ? StringUtil::Format("{}", *pegout_amount) : "INVALID",
                 kernel.GetFee()
             );
         };
@@ -154,4 +155,4 @@ class Transaction :
     mw::Hash m_hash;
 };
 
-END_NAMESPACE
\ No newline at end of file
+END_NAMESPACE
```

### src/libmw/include/mw/models/tx/TxBody.h
```diff
@@ -88,10 +88,10 @@ class TxBody : public Traits::ISerializable
     }
 
     std::vector<PegInCoin> GetPegIns() const noexcept;
-    CAmount GetPegInAmount() const noexcept;
+    boost::optional<CAmount> GetPegInAmount() const noexcept;
     std::vector<PegOutCoin> GetPegOuts() const noexcept;
-    CAmount GetTotalFee() const noexcept;
-    CAmount GetSupplyChange() const noexcept;
+    boost::optional<CAmount> GetTotalFee() const noexcept;
+    boost::optional<CAmount> GetSupplyChange() const noexcept;
     int32_t GetLockHeight() const noexcept;
 
     //
@@ -113,4 +113,4 @@ class TxBody : public Traits::ISerializable
 
     // List of kernels that make up this transaction.
     std::vector<Kernel> m_kernels;
-};
\ No newline at end of file
+};
```

### src/libmw/src/models/tx/TxBody.cpp
```diff
@@ -1,4 +1,5 @@
 #include <mw/models/tx/TxBody.h>
+#include <mw/consensus/Amount.h>
 #include <mw/exceptions/ValidationException.h>
 #include <mw/consensus/Params.h>
 #include <mw/consensus/Weight.h>
@@ -18,12 +19,23 @@ std::vector<PegInCoin> TxBody::GetPegIns() const noexcept
     return pegins;
 }
 
-CAmount TxBody::GetPegInAmount() const noexcept
+boost::optional<CAmount> TxBody::GetPegInAmount() const noexcept
 {
-    return std::accumulate(
-        m_kernels.cbegin(), m_kernels.cend(), (CAmount)0,
-        [](const CAmount sum, const auto& kernel) noexcept { return sum + kernel.GetPegIn(); }
-    );
+    CAmount total = 0;
+    for (const Kernel& kernel : m_kernels) {
+        if (!AmountUtil::IsValidMoney(kernel.GetPegIn())) {
+            return boost::none;
+        }
+
+        const auto next_total = AmountUtil::TrySafeAdd(total, kernel.GetPegIn());
+        if (!next_total || !AmountUtil::IsValidMoney(*next_total)) {
+            return boost::none;
+        }
+
+        total = *next_total;
+    }
+
+    return total;
 }
 
 std::vector<PegOutCoin> TxBody::GetPegOuts() const noexcept
@@ -37,20 +49,43 @@ std::vector<PegOutCoin> TxBody::GetPegOuts() const noexcept
     return pegouts;
 }
 
-CAmount TxBody::GetTotalFee() const noexcept
+boost::optional<CAmount> TxBody::GetTotalFee() const noexcept
 {
-    return std::accumulate(
-        m_kernels.cbegin(), m_kernels.cend(), (CAmount)0,
-        [](const CAmount sum, const auto& kernel) noexcept { return sum + kernel.GetFee(); }
-    );
+    CAmount total = 0;
+    for (const Kernel& kernel : m_kernels) {
+        if (!AmountUtil::IsValidMoney(kernel.GetFee())) {
+            return boost::none;
+        }
+
+        const auto next_total = AmountUtil::TrySafeAdd(total, kernel.GetFee());
+        if (!next_total || !AmountUtil::IsValidMoney(*next_total)) {
+            return boost::none;
+        }
+
+        total = *next_total;
+    }
+
+    return total;
 }
 
-CAmount TxBody::GetSupplyChange() const noexcept
+boost::optional<CAmount> TxBody::GetSupplyChange() const noexcept
 {
-    return std::accumulate(
-        m_kernels.cbegin(), m_kernels.cend(), (CAmount)0,
-        [](const CAmount supply_change, const auto& kernel) noexcept { return supply_change + kernel.GetSupplyChange(); }
-    );
+    CAmount total = 0;
+    for (const Kernel& kernel : m_kernels) {
+        const auto kernel_supply_change = kernel.GetSupplyChange();
+        if (!kernel_supply_change) {
+            return boost::none;
+        }
+
+        const auto next_total = AmountUtil::TrySafeAdd(total, *kernel_supply_change);
+        if (!next_total || !AmountUtil::IsValidAmountRange(*next_total)) {
+            return boost::none;
+        }
+
+        total = *next_total;
+    }
+
+    return total;
 }
 
 int32_t TxBody::GetLockHeight() const noexcept
@@ -131,4 +166,4 @@ void TxBody::Validate() const
     if (!Bulletproofs::BatchVerify(rangeProofs)) {
         ThrowValidation(EConsensusError::BULLETPROOF);
     }
-}
\ No newline at end of file
+}
```

### src/libmw/src/node/BlockBuilder.cpp
```diff
@@ -18,11 +18,16 @@ bool BlockBuilder::AddTransaction(const Transaction::CPtr& pTransaction, const s
     }
     
     // Verify pegin amount matches
-    const uint64_t actual_amount = pTransaction->GetPegInAmount();
-    const uint64_t expected_amount = std::accumulate(pegins.cbegin(), pegins.cend(), (uint64_t)0,
-        [](const uint64_t sum, const PegInCoin& pegin) { return sum + pegin.GetAmount(); }
+    const auto actual_amount = pTransaction->GetPegInAmount();
+    if (!actual_amount) {
+        LOG_ERROR("Invalid pegin amount");
+        return false;
+    }
+
+    const CAmount expected_amount = std::accumulate(pegins.cbegin(), pegins.cend(), (CAmount)0,
+        [](const CAmount sum, const PegInCoin& pegin) { return sum + pegin.GetAmount(); }
     );
-    if (actual_amount != expected_amount) {
+    if (*actual_amount != expected_amount) {
         LOG_ERROR("Mismatched pegin amount");
         return false;
     }
@@ -118,4 +123,4 @@ mw::Block::Ptr BlockBuilder::BuildBlock() const
     return mw::CoinsViewCache(m_pCoinsView).BuildNextBlock(m_height, m_stagedTxs);
 }
 
-END_NAMESPACE
\ No newline at end of file
+END_NAMESPACE
```

### src/libmw/test/tests/models/block/Test_Block.cpp
```diff
@@ -47,7 +47,9 @@ BOOST_AUTO_TEST_CASE(Block)
     BOOST_REQUIRE(block.GetStealthOffset() == pHeader->GetStealthOffset());
 
     BOOST_REQUIRE(block.GetPegIns() == pTransaction->GetPegIns());
-    BOOST_REQUIRE(block.GetPegInAmount() == 30);
+    const auto pegin_amount = block.GetPegInAmount();
+    BOOST_REQUIRE(pegin_amount.has_value());
+    BOOST_REQUIRE(*pegin_amount == 30);
     BOOST_REQUIRE(block.GetPegOuts().empty());
 
     std::vector<uint8_t> block_serialized = block.Serialized();
@@ -59,4 +61,4 @@ BOOST_AUTO_TEST_CASE(Block)
     block.Validate();
 }
 
-BOOST_AUTO_TEST_SUITE_END()
\ No newline at end of file
+BOOST_AUTO_TEST_SUITE_END()
```

### src/libmw/test/tests/models/tx/Test_Kernel.cpp
```diff
@@ -7,6 +7,8 @@
 
 #include <test_framework/TestMWEB.h>
 
+#include <limits>
+
 BOOST_FIXTURE_TEST_SUITE(TestKernel, MWEBTestingSetup)
 
 BOOST_AUTO_TEST_CASE(PlainKernel_Test)
@@ -102,4 +104,38 @@ BOOST_AUTO_TEST_CASE(NonStandardKernel_Test)
     BOOST_REQUIRE(!nonstandard_kernel2.IsStandard());
 }
 
-BOOST_AUTO_TEST_SUITE_END()
\ No newline at end of file
+BOOST_AUTO_TEST_CASE(PegOutAmountOutOfRange_Test)
+{
+    std::vector<uint8_t> script_bytes = secret_key_t<30>::Random().vec();
+    CScript script(script_bytes.data(), script_bytes.data() + script_bytes.size());
+
+    Kernel kernel = Kernel::Create(
+        BlindingFactor::Random(),
+        boost::none,
+        boost::none,
+        boost::none,
+        std::vector<PegOutCoin>{ PegOutCoin(MAX_MONEY, script), PegOutCoin(1, script) },
+        boost::none
+    );
+
+    BOOST_REQUIRE(!kernel.GetPegOutAmount().has_value());
+}
+
+BOOST_AUTO_TEST_CASE(SupplyChangeOutOfRange_Test)
+{
+    std::vector<uint8_t> script_bytes = secret_key_t<30>::Random().vec();
+    CScript script(script_bytes.data(), script_bytes.data() + script_bytes.size());
+
+    Kernel kernel = Kernel::Create(
+        BlindingFactor::Random(),
+        boost::none,
+        std::numeric_limits<CAmount>::max(),
+        boost::none,
+        std::vector<PegOutCoin>{ PegOutCoin(1, script) },
+        boost::none
+    );
+
+    BOOST_REQUIRE(!kernel.GetSupplyChange().has_value());
+}
+
+BOOST_AUTO_TEST_SUITE_END()
```
