# [?] llmq: harden DKG message-intake against unauthenticated retention and crashes

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-06-30
Source: https://github.com/dashpay/dash/commit/31142da98c8147b0d092d9fa0eff29def5a13b10
Type: security-commit

## Details
llmq: harden DKG message-intake against unauthenticated retention and crashes

Harden the pushed DKG message path (QCONTRIB/QCOMPLAINT/QJUSTIFICATION/QPCOMMITMENT):

- Require the sending peer to be MNAuth-verified (qwatch is unauthenticated and does not bypass this).

- Reject oversized DKG payloads (per-type MaxDKGMessageSize) before deserialization/retention.

- Structurally pre-validate (param-only checks, on a copy) before retention.

- Never feed an invalid BLS signature to CBLSSignature::AggregateInsecure(): the batch verifier skips invalid sigs and per-type PreVerifyMessage rejects them.

## Patch
### src/Makefile.am
```diff
@@ -277,6 +277,7 @@ BITCOIN_CORE_H = \
   llmq/commitment.h \
   llmq/context.h \
   llmq/debug.h \
+  llmq/dkgmessages.h \
   llmq/dkgsession.h \
   llmq/dkgsessionhandler.h \
   llmq/dkgsessionmgr.h \
```

### src/active/dkgsessionhandler.cpp
```diff
@@ -275,6 +275,18 @@ std::set<NodeId> BatchVerifyMessageSigs(CDKGSession& session, const std::vector<
             continue;
         }
 
+        // An invalid signature must never reach AggregateInsecure(), which asserts
+        // that both operands are valid. Mark the sender bad and skip it instead of
+        // aggregating it. This guard is mandatory: it covers every
+        // message type the batch verifier is instantiated for, including those whose
+        // per-message PreVerifyMessage does not (yet) reject invalid signatures.
+        // Note: 'first' below tracks the first *accumulated* (valid) signature, not
+        // the first *examined* message, so skipping leading invalid sigs is safe.
+        if (!msg->sig.IsValid()) {
+            ret.emplace(nodeId);
+            continue;
+        }
+
         if (first) {
             aggSig = msg->sig;
         } else {
@@ -298,6 +310,12 @@ std::set<NodeId> BatchVerifyMessageSigs(CDKGSession& session, const std::vector<
         messageHashes.emplace_back(msgHash);
     }
     if (!revertToSingleVerification) {
+        if (pubKeys.empty()) {
+            // Every message had an unknown member or invalid signature; all such
+            // senders are already in ret. VerifyInsecureAggregated() asserts that
+            // the pubkey/hash spans are non-empty, so bail out here.
+            return ret;
+        }
         if (aggSig.VerifyInsecureAggregated(pubKeys, messageHashes)) {
             // all good
             return ret;
@@ -322,6 +340,13 @@ std::set<NodeId> BatchVerifyMessageSigs(CDKGSession& session, const std::vector<
         }
 
         auto member = session.GetMember(msg->proTxHash);
+        if (member == nullptr || !msg->sig.IsValid()) {
+            // Examined messages with these properties are already in ret, but the
+            // early break on a duplicate hash above can leave some unexamined.
+            // Stay defensive: never dereference a null member or verify an invalid sig.
+            ret.emplace(nodeId);
+            continue;
+        }
         bool valid = msg->sig.VerifyInsecure(member->dmn->pdmnState->pubKeyOperator.Get(), msg->GetSignHash());
         if (!valid) {
             ret.emplace(nodeId);
```

### src/llmq/dkgmessages.h
```diff
@@ -0,0 +1,188 @@
+// Copyright (c) 2018-2025 The Dash Core developers
+// Distributed under the MIT/X11 software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#ifndef BITCOIN_LLMQ_DKGMESSAGES_H
+#define BITCOIN_LLMQ_DKGMESSAGES_H
+
+#include <llmq/commitment.h>
+
+#include <bls/bls_ies.h>
+#include <hash.h>
+#include <serialize.h>
+#include <util/underlying.h>
+
+#include <algorithm>
+#include <memory>
+#include <vector>
+
+namespace llmq {
+class CDKGContribution
+{
+public:
+    Consensus::LLMQType llmqType;
+    uint256 quorumHash;
+    uint256 proTxHash;
+    BLSVerificationVectorPtr vvec;
+    std::shared_ptr<CBLSIESMultiRecipientObjects<CBLSSecretKey>> contributions;
+    CBLSSignature sig;
+
+public:
+    template <typename Stream>
+    inline void SerializeWithoutSig(Stream& s) const
+    {
+        s << ToUnderlying(llmqType);
+        s << quorumHash;
+        s << proTxHash;
+        s << *vvec;
+        s << *contributions;
+    }
+    template <typename Stream>
+    inline void Serialize(Stream& s) const
+    {
+        SerializeWithoutSig(s);
+        s << sig;
+    }
+    template <typename Stream>
+    inline void Unserialize(Stream& s)
+    {
+        std::vector<CBLSPublicKey> tmp1;
+        CBLSIESMultiRecipientObjects<CBLSSecretKey> tmp2;
+
+        s >> llmqType;
+        s >> quorumHash;
+        s >> proTxHash;
+        s >> tmp1;
+        s >> tmp2;
+        s >> sig;
+
+        vvec = std::make_shared<std::vector<CBLSPublicKey>>(std::move(tmp1));
+        contributions = std::make_shared<CBLSIESMultiRecipientObjects<CBLSSecretKey>>(std::move(tmp2));
+    }
+
+    [[nodiscard]] uint256 GetSignHash() const
+    {
+        CHashWriter hw(SER_GETHASH, 0);
+        SerializeWithoutSig(hw);
+        hw << CBLSSignature();
+        return hw.GetHash();
+    }
+};
+
+class CDKGComplaint
+{
+public:
+    Consensus::LLMQType llmqType{Consensus::LLMQType::LLMQ_NONE};
+    uint256 quorumHash;
+    uint256 proTxHash;
+    std::vector<bool> badMembers;
+    std::vector<bool> complainForMembers;
+    CBLSSignature sig;
+
+public:
+    CDKGComplaint() = default;
+    explicit CDKGComplaint(const Consensus::LLMQParams& params) :
+            badMembers((size_t)params.size), complainForMembers((size_t)params.size) {};
+
+    SERIALIZE_METHODS(CDKGComplaint, obj)
+    {
+        READWRITE(
+                obj.llmqType,
+                obj.quorumHash,
+                obj.proTxHash,
+                DYNBITSET(obj.badMembers),
+                DYNBITSET(obj.complainForMembers),
+                obj.sig
+                );
+    }
+
+    [[nodiscard]] uint256 GetSignHash() const
+    {
+        CDKGComplaint tmp(*this);
+        tmp.sig = CBLSSignature();
+        return ::SerializeHash(tmp);
+    }
+};
+
+class CDKGJustification
+{
+public:
+    Consensus::LLMQType llmqType;
+    uint256 quorumHash;
+    uint256 proTxHash;
+    struct Contribution {
+        uint32_t index;
+        CBLSSecretKey key;
+        SERIALIZE_METHODS(Contribution, obj)
+        {
+            READWRITE(obj.index, obj.key);
+        }
+    };
+    std::vector<Contribution> contributions;
+    CBLSSignature sig;
+
+public:
+    SERIALIZE_METHODS(CDKGJustification, obj)
+    {
+        READWRITE(obj.llmqType, obj.quorumHash, obj.proTxHash, obj.contributions, obj.sig);
+    }
+
+    [[nodiscard]] uint256 GetSignHash() const
+    {
+        CDKGJustification tmp(*this);
+        tmp.sig = CBLSSignature();
+        return ::SerializeHash(tmp);
+    }
+};
+
+// each member commits to a single set of valid members with this message
+// then each node aggregate all received premature commitments
+// into a single CFinalCommitment, which is only valid if
+// enough (>=minSize) premature commitments were aggregated
+class CDKGPrematureCommitment
+{
+public:
+    Consensus::LLMQType llmqType{Consensus::LLMQType::LLMQ_NONE};
+    uint256 quorumHash;
+    uint256 proTxHash;
+    std::vector<bool> validMembers;
+
+    CBLSPublicKey quorumPublicKey;
+    uint256 quorumVvecHash;
+
+    CBLSSignature quorumSig; // threshold sig share of quorumHash+validMembers+pubKeyHash+vvecHash
+    CBLSSignature sig; // single member sig of quorumHash+validMembers+pubKeyHash+vvecHash
+
+public:
+    CDKGPrematureCommitment() = default;
+    explicit CDKGPrematureCommitment(const Consensus::LLMQParams& params) :
+            validMembers((size_t)params.size) {};
+
+    [[nodiscard]] int CountValidMembers() const
+    {
+        return int(std::count(validMembers.begin(), validMembers.end(), true));
+    }
+
+public:
+    SERIALIZE_METHODS(CDKGPrematureCommitment, obj)
+    {
+        READWRITE(
+                obj.llmqType,
+                obj.quorumHash,
+                obj.proTxHash,
+                DYNBITSET(obj.validMembers),
+                obj.quorumPublicKey,
+                obj.quorumVvecHash,
+                obj.quorumSig,
+                obj.sig
+                );
+    }
+
+    [[nodiscard]] uint256 GetSignHash() const
+    {
+        return BuildCommitmentHash(llmqType, quorumHash, validMembers, quorumPublicKey, quorumVvecHash);
+    }
+};
+} // namespace llmq
+
+#endif // BITCOIN_LLMQ_DKGMESSAGES_H
```

### src/llmq/dkgsession.cpp
```diff
@@ -169,6 +169,15 @@ bool CDKGSession::PreVerifyMessage(const CDKGContribution& qc, bool& retBan) con
         return false;
     }
 
+    // Reject a structurally-invalid (e.g. all-zero) signature here. This is a cheap
+    // validity check, not the batched signature verification; it ensures the message
+    // never reaches CBLSSignature::AggregateInsecure(), which asserts validity.
+    if (!qc.sig.IsValid()) {
+        logger.Batch("invalid contribution signature");
+        retBan = true;
+        return false;
+    }
+
     if (qc.contributions->blobs.size() != members.size()) {
         logger.Batch("invalid contributions count");
         retBan = true;
@@ -299,6 +308,14 @@ bool CDKGSession::PreVerifyMessage(const CDKGComplaint& qc, bool& retBan) const
         return false;
     }
 
+    // Cheap validity check (not the batched signature verification): reject a
+    // structurally-invalid signature before it can reach AggregateInsecure().
+    if (!qc.sig.IsValid()) {
+        logger.Batch("invalid complaint signature");
+        retBan = true;
+        return false;
+    }
+
     if (qc.badMembers.size() != (size_t)params.size) {
         logger.Batch("invalid badMembers bitset size");
         retBan = true;
@@ -403,6 +420,14 @@ bool CDKGSession::PreVerifyMessage(const CDKGJustification& qj, bool& retBan) co
         return false;
     }
 
+    // Cheap validity check (not the batched signature verification): reject a
+    // structurally-invalid signature before it can reach AggregateInsecure().
+    if (!qj.sig.IsValid()) {
+        logger.Batch("invalid justification signature");
+        retBan = true;
+        return false;
+    }
+
     if (qj.contributions.empty()) {
         logger.Batch("justification with no contributions");
         retBan = true;
```

### src/llmq/dkgsession.h
```diff
@@ -5,7 +5,7 @@
 #ifndef BITCOIN_LLMQ_DKGSESSION_H
 #define BITCOIN_LLMQ_DKGSESSION_H
 
-#include <llmq/commitment.h>
+#include <llmq/dkgmessages.h>
 
 #include <batchedlogger.h>
 #include <bls/bls.h>
@@ -39,173 +39,6 @@ class CQuorumSnapshotManager;
 } // namespace llmq
 
 namespace llmq {
-class CDKGContribution
-{
-public:
-    Consensus::LLMQType llmqType;
-    uint256 quorumHash;
-    uint256 proTxHash;
-    BLSVerificationVectorPtr vvec;
-    std::shared_ptr<CBLSIESMultiRecipientObjects<CBLSSecretKey>> contributions;
-    CBLSSignature sig;
-
-public:
-    template<typename Stream>
-    inline void SerializeWithoutSig(Stream& s) const
-    {
-        s << ToUnderlying(llmqType);
-        s << quorumHash;
-        s << proTxHash;
-        s << *vvec;
-        s << *contributions;
-    }
-    template<typename Stream>
-    inline void Serialize(Stream& s) const
-    {
-        SerializeWithoutSig(s);
-        s << sig;
-    }
-    template<typename Stream>
-    inline void Unserialize(Stream& s)
-    {
-        std::vector<CBLSPublicKey> tmp1;
-        CBLSIESMultiRecipientObjects<CBLSSecretKey> tmp2;
-
-        s >> llmqType;
-        s >> quorumHash;
-        s >> proTxHash;
-        s >> tmp1;
-        s >> tmp2;
-        s >> sig;
-
-        vvec = std::make_shared<std::vector<CBLSPublicKey>>(std::move(tmp1));
-        contributions = std::make_shared<CBLSIESMultiRecipientObjects<CBLSSecretKey>>(std::move(tmp2));
-    }
-
-    [[nodiscard]] uint256 GetSignHash() const
-    {
-        CHashWriter hw(SER_GETHASH, 0);
-        SerializeWithoutSig(hw);
-        hw << CBLSSignature();
-        return hw.GetHash();
-    }
-};
-
-class CDKGComplaint
-{
-public:
-    Consensus::LLMQType llmqType{Consensus::LLMQType::LLMQ_NONE};
-    uint256 quorumHash;
-    uint256 proTxHash;
-    std::vector<bool> badMembers;
-    std::vector<bool> complainForMembers;
-    CBLSSignature sig;
-
-public:
-    CDKGComplaint() = default;
-    explicit CDKGComplaint(const Consensus::LLMQParams& params) :
-            badMembers((size_t)params.size), complainForMembers((size_t)params.size) {};
-
-    SERIALIZE_METHODS(CDKGComplaint, obj)
-    {
-        READWRITE(
-                obj.llmqType,
-                obj.quorumHash,
-                obj.proTxHash,
-                DYNBITSET(obj.badMembers),
-                DYNBITSET(obj.complainForMembers),
-                obj.sig
-                );
-    }
-
-    [[nodiscard]] uint256 GetSignHash() const
-    {
-        CDKGComplaint tmp(*this);
-        tmp.sig = CBLSSignature();
-        return ::SerializeHash(tmp);
-    }
-};
-
-class CDKGJustification
-{
-public:
-    Consensus::LLMQType llmqType;
-    uint256 quorumHash;
-    uint256 proTxHash;
-    struct Contribution {
-        uint32_t index;
-        CBLSSecretKey key;
-        SERIALIZE_METHODS(Contribution, obj)
-        {
-            READWRITE(obj.index, obj.key);
-        }
-    };
-    std::vector<Contribution> contributions;
-    CBLSSignature sig;
-
-public:
-    SERIALIZE_METHODS(CDKGJustification, obj)
-    {
-        READWRITE(obj.llmqType, obj.quorumHash, obj.proTxHash, obj.contributions, obj.sig);
-    }
-
-    [[nodiscard]] uint256 GetSignHash() const
-    {
-        CDKGJustification tmp(*this);
-        tmp.sig = CBLSSignature();
-        return ::SerializeHash(tmp);
-    }
-};
-
-// each member commits to a single set of valid members with this message
-// then each node aggregate all received premature commitments
-// into a single CFinalCommitment, which is only valid if
-// enough (>=minSize) premature commitments were aggregated
-class CDKGPrematureCommitment
-{
-public:
-    Consensus::LLMQType llmqType{Consensus::LLMQType::LLMQ_NONE};
-    uint256 quorumHash;
-    uint256 proTxHash;
-    std::vector<bool> validMembers;
-
-    CBLSPublicKey quorumPublicKey;
-    uint256 quorumVvecHash;
-
-    CBLSSignature quorumSig; // threshold sig share of quorumHash+validMembers+pubKeyHash+vvecHash
-    CBLSSignature sig; // single member sig of quorumHash+validMembers+pubKeyHash+vvecHash
-
-public:
-    CDKGPrematureCommitment() = default;
-    explicit CDKGPrematureCommitment(const Consensus::LLMQParams& params) :
-            validMembers((size_t)params.size) {};
-
-    [[nodiscard]] int CountValidMembers() const
-    {
-        return int(std::count(validMembers.begin(), validMembers.end(), true));
-    }
-
-public:
-    SERIALIZE_METHODS(CDKGPrematureCommitment, obj)
-    {
-        READWRITE(
-                obj.llmqType,
-                obj.quorumHash,
-                obj.proTxHash,
-                DYNBITSET(obj.validMembers),
-                obj.quorumPublicKey,
-                obj.quorumVvecHash,
-                obj.quorumSig,
-                obj.sig
-                );
-    }
-
-    [[nodiscard]] uint256 GetSignHash() const
-    {
-        return BuildCommitmentHash(llmqType, quorumHash, validMembers, quorumPublicKey, quorumVvecHash);
-    }
-};
-
 class CDKGMember
 {
 public:
```

### src/llmq/dkgsessionmgr.cpp
```diff
@@ -3,6 +3,7 @@
 // file COPYING or http://www.opensource.org/licenses/mit-license.php.
 
 #include <llmq/dkgsessionmgr.h>
+#include <llmq/dkgmessages.h>
 #include <llmq/options.h>
 #include <llmq/params.h>
 #include <llmq/utils.h>
@@ -29,6 +30,86 @@ static const std::string DB_VVEC = "qdkg_V";
 static const std::string DB_SKCONTRIB = "qdkg_S";
 static const std::string DB_ENC_CONTRIB = "qdkg_E";
 
+namespace {
+// Upper bound on the serialized size of a well-formed DKG message of the given
+// type for the given quorum params. Used to reject oversized payloads at intake
+// before any deserialization or retention, which closes the low-cost memory
+// amplification window (a legitimate message is bounded by quorum params, far
+// below the 3 MiB transport cap). Generous slack is added and the result is
+// clamped to a hard ceiling so a future params change can never silently re-open
+// the full transport window.
+size_t MaxDKGMessageSize(std::string_view msg_type, const Consensus::LLMQParams& params)
+{
+    constexpr size_t COMPACT = 5;          // max CompactSize for any realistic count
+    constexpr size_t PREFIX = 1 + 32 + 32; // llmqType + quorumHash + proTxHash
+    constexpr size_t PUBKEY = BLS_CURVE_PUBKEY_SIZE; // 48
+    constexpr size_t SIG = BLS_CURVE_SIG_SIZE;       // 96
+    constexpr size_t SECKEY = BLS_CURVE_SECKEY_SIZE; // 32
+    constexpr size_t BLOB = COMPACT + 128; // encrypted seckey blob, generous
+    constexpr size_t SLACK = 1024;
+    constexpr size_t HARD_CEILING = size_t{1} << 20; // 1 MiB
+
+    const size_t size = params.size > 0 ? static_cast<size_t>(params.size) : 0;
+    const size_t threshold = params.threshold > 0 ? static_cast<size_t>(params.threshold) : 0;
+
+    size_t cap = 0;
+    if (msg_type == NetMsgType::QCONTRIB) {
+        // llmqType/quorumHash/proTxHash + vvec + contributions(IES) + sig
+        cap = PREFIX + (COMPACT + threshold * PUBKEY) + (PUBKEY + 32 + COMPACT + size * BLOB) + SIG;
+    } else if (msg_type == NetMsgType::QJUSTIFICATION) {
+        // ... + contributions(index u32 + seckey) + sig
+        cap = PREFIX + (COMPACT + size * (4 + SECKEY)) + SIG;
+    } else if (msg_type == NetMsgType::QCOMPLAINT) {
+        // ... + 2 dynamic bitsets (badMembers, complainForMembers) + sig
+        cap = PREFIX + 2 * (COMPACT + (size + 7) / 8) + SIG;
+    } else if (msg_type == NetMsgType::QPCOMMITMENT) {
+        // ... + validMembers bitset + quorumPublicKey + quorumVvecHash + quorumSig + sig
+        cap = PREFIX + (COMPACT + (size + 7) / 8) + PUBKEY + 32 + 2 * SIG;
+    } else {
+        return HARD_CEILING;
+    }
+    cap += SLACK;
+    return cap < HARD_CEILING ? cap : HARD_CEILING;
+}
+
+// Cheap, param-only structural validation of a pushed DKG message, run at intake
+// before retention. Deserializes a COPY of the payload (leaving the caller's bytes
+// intact for the pending queue and its inventory hash) and checks only invariants
+// derived from quorum params: no member-list lookup and no signature verification,
+// which remain on the DKG worker thread. Deserializing the copy does decompress the
+// BLS points carried in the payload, but that work is bounded by the size cap applied
+// just before this check. Rejects malformed or wrong-shaped payloads before retention.
+bool CheckDKGMessageStructure(std::string_view msg_type, const CDataStream& vRecv, const Consensus::LLMQParams& params)
+{
+    const size_t size = params.size > 0 ? static_cast<size_t>(params.size) : 0;
+    const size_t threshold = params.threshold > 0 ? static_cast<size_t>(params.threshold) : 0;
+    try {
+        CDataStream s(vRecv); // copy; deserialization does not advance the caller's stream
+        if (msg_type == NetMsgType::QCONTRIB) {
+            CDKGContribution qc;
+            s >> qc;
+            return qc.vvec != nullptr && qc.vvec->size() == threshold &&
+                   qc.contributions != nullptr && qc.contributions->blobs.size() == size;
+        } else if (msg_type == NetMsgType::QCOMPLAINT) {
+            CDKGComplaint qc;
+            s >> qc;
+            return qc.badMembers.size() == size && qc.complainForMembers.size() == size;
+        } else if (msg_type == NetMsgType::QJUSTIFICATION) {
+            CDKGJustification qj;
+            s >> qj;
+            return qj.contributions.size() <= size;
+        } else if (msg_type == NetMsgType::QPCOMMITMENT) {
+            CDKGPrematureCommitment qc;
+            s >> qc;
+            return qc.validMembers.size() == size;
+        }
+        return false;
+    } catch (const std::exception&) {
+        return false;
+    }
+}
+} // anonymous namespace
+
 CDKGSessionManager::CDKGSessionManager(CDeterministicMNManager& dmnman, CQuorumSnapshotManager& qsnapman,
                                        const ChainstateManager& chainman, const CSporkManager& sporkman,
                                        const util::DbWrapperParams& db_params, bool quorums_watch) :
@@ -104,6 +185,14 @@ MessageProcessingResult CDKGSessionManager::ProcessMessage(CNode& pfrom, bool is
         return MisbehavingError{10};
     }
 
+    // Pushed DKG messages (QCONTRIB/QCOMPLAINT/QJUSTIFICATION/QPCOMMITMENT) retain
+    // attacker-controlled payloads, so they must originate from an MNAuth-verified
+    // masternode. qwatch is unauthenticated (any peer can set it via QWATCH) and is
+    // only meaningful for pull/observation paths; it must not bypass this gate.
+    if (pfrom.GetVerifiedProRegTxHash().IsNull()) {
+        return MisbehavingError{10, "DKG message from non-verified peer"};
+    }
+
     if (vRecv.empty()) {
         return MisbehavingError{100};
     }
@@ -164,6 +253,20 @@ MessageProcessingResult CDKGSessionManager::ProcessMessage(CNode& pfrom, bool is
     }
 
     assert(quorumIndex != -1);
+
+    // Reject oversized payloads before any deserialization or retention. A
+    // well-formed DKG message is bounded by quorum params; anything larger is an
+    // amplification attempt against the per-peer pending queue.
+    if (vRecv.size() > MaxDKGMessageSize(msg_type, llmq_params)) {
+        return MisbehavingError{100, "oversized DKG message"};
+    }
+
+    // Cheap structural pre-validation before retention. Validates a copy so the
+    // original bytes (and their inventory hash) are preserved for the worker.
+    if (!CheckDKGMessageStructure(msg_type, vRecv, llmq_params)) {
+        return MisbehavingError{100, "malformed DKG message"};
+    }
+
     WITH_LOCK(cs_indexedQuorumsCache, indexedQuorumsCache[llmqType].insert(quorumHash, quorumIndex));
     return Assert(dkgSessionHandlers.at({llmqType, quorumIndex}))->ProcessMessage(pfrom.GetId(), msg_type, vRecv);
 }
```

### test/functional/feature_llmq_dkg_intake.py
```diff
@@ -0,0 +1,149 @@
+#!/usr/bin/env python3
+# Copyright (c) 2026 The Dash Core developers
+# Distributed under the MIT software license, see the accompanying
+# file COPYING or http://www.opensource.org/licenses/mit-license.php.
+"""
+feature_llmq_dkg_intake.py
+
+Adversarial P2P tests for DKG message-intake hardening:
+  - pushed DKG messages (qcontrib/qcomplaint/qjustify/qpcommit) from a peer that is
+    not MNAuth-verified are rejected before retention.
+  - oversized DKG payloads are rejected (before deserialization / retention) even
+    from a verified peer.
+  - structural pre-validation: malformed DKG payloads (valid quorum prefix, garbage
+    body) are rejected before retention even from a verified peer.
+
+The node must not crash; the sending peer must be scored (Misbehaving).
+"""
+
+from test_framework.messages import ser_uint256
+from test_framework.p2p import P2PInterface
+from test_framework.test_framework import DashTestFramework
+from test_framework.util import wait_until_helper
+
+LLMQ_TEST = 100
+
+# A masternode protx/operator-pubkey pair accepted by the regtest-only `mnauth`
+# debug RPC, used to mark a P2P connection as MNAuth-verified without BLS signing.
+FAKE_PROTX = "cecf37bf0ec05d2d22cb8227f88074bb882b94cd2081ba318a5a444b1b15b9fd"
+FAKE_PUBKEY = "8e7afdb849e5e2a085b035b62e21c0940c753f2d4501325743894c37162f287bccaffbedd60c36581dabbf127a22e43f"
+
+DKG_PUSH_TYPES = [b"qcontrib", b"qcomplaint", b"qjustify", b"qpcommit"]
+
+
+class msg_dkg_raw:
+    """A DKG push message carrying an arbitrary raw payload (for adversarial intake tests)."""
+    __slots__ = ("msgtype", "payload")
+
+    def __init__(self, msgtype, payload=b""):
+        self.msgtype = msgtype
+        self.payload = payload
+
+    def serialize(self):
+        return self.payload
+
+    def __repr__(self):
+        return "msg_dkg_raw(type=%s, len=%d)" % (self.msgtype, len(self.payload))
+
+
+def get_p2p_id(node):
+    def get_id():
+        for p in node.getpeerinfo():
+            for p2p in node.p2ps:
+                if p["subver"] == p2p.strSubVer:
+                    return p["id"]
+        return None
+    wait_until_helper(lambda: get_id() is not None, timeout=10)
+    return get_id()
+
+
+def wait_for_banscore(node, peer_id, expected_score):
+    def get_score():
+        for peer in node.getpeerinfo():
+            if peer["id"] == peer_id:
+                return peer["banscore"]
+        return None
+    wait_until_helper(lambda: get_score() == expected_score, timeout=10)
+
+
+class DkgIntakeTest(DashTestFramework):
+    def add_options(self, parser):
+        self.add_wallet_options(parser)
+
+    def set_test_params(self):
+        # -whitelist keeps the adversarial peer connected even after it crosses the
+        #   discouragement threshold, so banscore stays observable for the score==100 cases.
+        # -debug=net surfaces the Misbehaving reason strings in debug.log.
+        extra_args = [["-whitelist=127.0.0.1", "-debug=net", "-deprecatedrpc=banscore"]] * 4
+        self.set_dash_test_params(4, 3, extra_args=extra_args)
+
+    def quorum_hash_prefix(self):
+        # llmqType (1 byte) + quorumHash (32 bytes, little-endian) -- the on-wire prefix
+        # shared by every DKG message, used so oversized/malformed payloads resolve to a
+        # real in-progress quorum and reach the size/structural checks.
+        return bytes([LLMQ_TEST]) + ser_uint256(int(self.quorum_hash, 16))
+
+    def add_verified_peer(self, node):
+        peer = node.add_p2p_connection(P2PInterface())
+        peer_id = get_p2p_id(node)
+        assert node.mnauth(peer_id, FAKE_PROTX, FAKE_PUBKEY)
+        return peer, peer_id
+
+    def run_test(self):
+        node0 = self.nodes[0]
+        node0.sporkupdate("SPORK_17_QUORUM_DKG_ENABLED", 0)
+        self.wait_for_sporks_same()
+
+        # Mine a quorum so we have a quorumHash that resolves to a valid DKG base block.
+        self.quorum_hash = self.mine_quorum()
+
+        # Target an active masternode -- the realistic victim of these messages.
+        mn_node = self.mninfo[0].get_node(self)
+
+        self.test_unverified_sender_rejected(mn_node)
+        self.test_oversized_rejected(mn_node)
+        self.test_malformed_rejected(mn_node)
+
+    def test_unverified_sender_rejected(self, node):
+        self.log.info("Pushed DKG messages from a non-verified peer are rejected (Misbehaving 10 each)")
+        peer = node.add_p2p_connection(P2PInterface())
+        peer_id = get_p2p_id(node)
+        wait_for_banscore(node, peer_id, 0)
+        score = 0
+        for msgtype in DKG_PUSH_TYPES:
+            with node.assert_debug_log(["DKG message from non-verified peer"]):
+                peer.send_message(msg_dkg_raw(msgtype, self.quorum_hash_prefix()))
+                peer.sync_with_ping()
+            score += 10
+            wait_for_banscore(node, peer_id, score)
+        node.disconnect_p2ps()
+
+    def test_oversized_rejected(self, node):
+        self.log.info("Oversized DKG payloads are rejected even from a verified peer (Misbehaving 100)")
+        peer, peer_id = self.add_verified_peer(node)
+        wait_for_banscore(node, peer_id, 0)
+        # >1 MiB clears the hard ceiling regardless of quorum params, and stays under the
+        # 3 MiB transport cap so the message is delivered to the handler.
+        payload = self.quorum_hash_prefix() + b"\x00" * (1024 * 1024 + 4096)
+        with node.assert_debug_log(["oversized DKG message"]):
+            peer.send_message(msg_dkg_raw(b"qcontrib", payload))
+            peer.sync_with_ping()
+        wait_for_banscore(node, peer_id, 100)
+        node.disconnect_p2ps()
+
+    def test_malformed_rejected(self, node):
+        self.log.info("Malformed DKG payloads are rejected even from a verified peer (Misbehaving 100)")
+        peer, peer_id = self.add_verified_peer(node)
+        wait_for_banscore(node, peer_id, 0)
+        # Valid llmqType + quorumHash prefix, then too few bytes to deserialize a
+        # CDKGContribution -> structural pre-validation rejects it before retention.
+        payload = self.quorum_hash_prefix() + b"\x00\x00\x00\x00"
+        with node.assert_debug_log(["malformed DKG message"]):
+            peer.send_message(msg_dkg_raw(b"qcontrib", payload))
+            peer.sync_with_ping()
+        wait_for_banscore(node, peer_id, 100)
+        node.disconnect_p2ps()
+
+
+if __name__ == '__main__':
+    DkgIntakeTest().main()
```

### test/functional/test_runner.py
```diff
@@ -137,6 +137,7 @@
     'feature_llmq_evo.py', # NOTE: needs dash_hash to pass
     'feature_llmq_is_cl_conflicts.py', # NOTE: needs dash_hash to pass
     'feature_llmq_dkgerrors.py', # NOTE: needs dash_hash to pass
+    'feature_llmq_dkg_intake.py', # NOTE: needs dash_hash to pass
     'feature_llmq_singlenode.py', # NOTE: needs dash_hash to pass
     'feature_dip4_coinbasemerkleroots.py', # NOTE: needs dash_hash to pass
     'feature_mnehf.py', # NOTE: needs dash_hash to pass
```
