# [?] Double Spend Proof (dsproof-beta) core code

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-01-25
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/0f7c703dd6f358a6c5ef67da497a51d867d2834b
Type: security-commit

## Details
Double Spend Proof (dsproof-beta) core code

Co-authored-by: Calin Culianu <calin.culianu@gmail.com>

The double spend proof code detects double spends, sends an INV to peers
and handles getdata requests by introducing a new 'dsproof-beta' message.

This adds a DoubleSpendProof and a DoubleSpendProofStorage set of classes
which are as you'd expect. The storage is owned by the mempool and the
mempool will delete DSPs from the DSPStorage as the transaction they
belong to go away (for instance if they are mined). The link between a
transaction in the mempool and its proof are by an addition to the
CTxMemPoolEntry class.

The dsproof related classes can be found within `src/dsproof/`.

Known limitation: the code currently only manages to create DSPs when
the UTXO it double spends is a p2pkh. This helps for the majority of the
cases on the net, but this issue is the main reason we have the name
'beta' in the message name.

For tests and documentation please refer to subsequent commits.

Test plan (for these core code changes only):
- build using the various ways (cmake and autoconf)
- run the unit and extended functional tests to verify nothing broke
  (all tests should still pass)

## Patch
### src/CMakeLists.txt
```diff
@@ -481,6 +481,11 @@ add_library(server
 	consensus/activation.cpp
 	consensus/tx_verify.cpp
 	consensus/tx_check.cpp
+	dsproof/dsproof.cpp
+	dsproof/dsproof_create.cpp
+	dsproof/dsproof_validate.cpp
+	dsproof/storage.cpp
+	dsproof/storage_cleanup.cpp
 	dbwrapper.cpp
 	flatfile.cpp
 	gbtlight.cpp
```

### src/Makefile.am
```diff
@@ -143,6 +143,9 @@ BITCOIN_CORE_H = \
   core_io.h \
   core_memusage.h \
   cuckoocache.h \
+  dsproof/dspid.h \
+  dsproof/dsproof.h \
+  dsproof/storage.h \
   extversion.h \
   flatfile.h \
   fs.h \
@@ -169,6 +172,7 @@ BITCOIN_CORE_H = \
   merkleblock.h \
   miner.h \
   net.h \
+  net_nodeid.h \
   net_permissions.h \
   net_processing.h \
   netaddress.h \
@@ -272,6 +276,11 @@ libbitcoin_server_a_SOURCES = \
   config.cpp \
   consensus/activation.cpp \
   consensus/tx_verify.cpp \
+  dsproof/dsproof.cpp \
+  dsproof/dsproof_create.cpp \
+  dsproof/dsproof_validate.cpp \
+  dsproof/storage.cpp \
+  dsproof/storage_cleanup.cpp \
   flatfile.cpp \
   gbtlight.cpp \
   httprpc.cpp \
```

### src/consensus/validation.h
```diff
@@ -6,7 +6,11 @@
 #ifndef BITCOIN_CONSENSUS_VALIDATION_H
 #define BITCOIN_CONSENSUS_VALIDATION_H
 
+#include <uint256.h>
+
 #include <string>
+#include <memory>
+#include <vector>
 
 /** "reject" message codes */
 static const uint8_t REJECT_MALFORMED = 0x01;
@@ -24,17 +28,50 @@ class CValidationState {
         MODE_VALID,   //!< everything ok
         MODE_INVALID, //!< network rule violation (DoS value may be set)
         MODE_ERROR,   //!< run-time error
-    } mode;
-    int nDoS;
+    } mode = MODE_VALID;
+    int nDoS = 0;
     std::string strRejectReason;
-    unsigned int chRejectCode;
-    bool corruptionPossible;
+    unsigned int chRejectCode = 0;
+    bool corruptionPossible = false;
     std::string strDebugMessage;
 
+    /// Validation data related to DoubleSpendProof
+    struct DoubleSpend {
+        /// DspId of the doublespend proof if the validation of the transaction resulted in a doublespend proof.
+        /// Note: hash.IsNull() may be true, in which case validation did not result in a doublespend proof.
+        uint256 hash;
+        /// Validation of transaction revealed non-validating-dsproof orphans(s), sent originally from these peers.
+        /// The ids in this vector may refer to peers which are no longer connected.
+        /// These ids will always be peers for which HasPermission(PF_NOBAN) == false (if they are still connected).
+        std::vector<int64_t> badNodeIds;
+    };
+    // The most common case is that *no* DSP exists. In order to minimize the memory/CPU footprint of the
+    // DSProof facility, we wrap this data in a unique_ptr which will be empty in the common case.
+    std::unique_ptr<DoubleSpend> dsp;
+    void dspCreateIfNotExist() { if (!dsp) dsp = std::make_unique<DoubleSpend>(); }
+
 public:
-    CValidationState()
-        : mode(MODE_VALID), nDoS(0), chRejectCode(0),
-          corruptionPossible(false) {}
+    CValidationState() = default;
+    CValidationState(const CValidationState &o) { *this = o; }
+    CValidationState(CValidationState &&) = default;
+
+    /// Copy-assignment must be custom-defined due to the presense of unique_ptr (must update this if adding fields!)
+    CValidationState &operator=(const CValidationState &o) {
+        mode = o.mode;
+        nDoS = o.nDoS;
+        strRejectReason = o.strRejectReason;
+        chRejectCode = o.chRejectCode;
+        corruptionPossible = o.corruptionPossible;
+        strDebugMessage = o.strDebugMessage;
+        if (o.dsp)
+            dsp = std::make_unique<DoubleSpend>(*o.dsp); // deep-copy the proof info
+        else
+            dsp.reset();
+        return *this;
+    }
+
+    /// Default move-assignment works ok for this class.
+    CValidationState &operator=(CValidationState &&) = default;
 
     bool DoS(int level, bool ret = false, unsigned int chRejectCodeIn = 0,
              const std::string &strRejectReasonIn = "",
@@ -83,6 +120,22 @@ class CValidationState {
     unsigned int GetRejectCode() const { return chRejectCode; }
     std::string GetRejectReason() const { return strRejectReason; }
     std::string GetDebugMessage() const { return strDebugMessage; }
+
+    // DoubleSpendProof getters and setters
+    bool HasDSPHash() const { return dsp && !dsp->hash.IsNull(); }
+    bool HasDSPBadNodeIds() const { return dsp && !dsp->badNodeIds.empty(); }
+    uint256 GetDSPHash() const { return dsp ? dsp->hash : uint256{}; }
+    std::vector<int64_t> GetDSPBadNodeIds() const { return dsp ? dsp->badNodeIds : decltype(dsp->badNodeIds){}; }
+    void SetDSPHash(const uint256 &dspHash) {
+        dspCreateIfNotExist();
+        dsp->hash = dspHash;
+    }
+    void PushDSPBadNodeId(int64_t nId) {
+        if (nId > -1) {
+            dspCreateIfNotExist();
+            dsp->badNodeIds.push_back(nId);
+        }
+    }
 };
 
 #endif // BITCOIN_CONSENSUS_VALIDATION_H
```

### src/dsproof/dspid.h
```diff
@@ -0,0 +1,112 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020-2021 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+#ifndef BITCOIN_DSPROOF_DSPID_H
+#define BITCOIN_DSPROOF_DSPID_H
+
+#include <uint256.h>
+
+#include <memory>
+
+
+//! Unique identifier for a DoubleSpend proof.
+//! It is just the hash of the serialized data structure.
+using DspId = uint256;
+
+
+//! A unique_ptr<DspId> work-alike that supports copy construction/assignment.
+//!
+//! Notes:
+//! - Copying/assigning creates a deep-copy (duplicate) of the underlying DspId
+//! - Copying/assigning of a DspId that .IsNull() will result in this class
+//!   holding a nullptr, as a memory saving technique, since .IsNull() DspId's
+//!   are semantically equivalent to a DspId that is not valid and/or does not
+//!   exist.
+//! - Unlike unique_ptr, comaprison operators always do a deep-compare of the
+//!   pointed-to DspId, with nullptr being semantically equivalend to an IsNull()
+//!   DspId. Comparing nullptr DspIdPtrs is supported.
+//!
+//! This class is intended to be used as an instance member for long-lived
+//! types such as CTxMemPoolEntry. Use of this class saves memory in the
+//! common-case of no DspId associated with the instance.
+//!
+//! This class takes only 8 bytes of memory on 64-bit, in the common-case of
+//! no valid DspId, as compared to a direct DspId instance which would
+//! take 32 bytes always, even if there is no associated double-spend proof.
+class DspIdPtr final {
+    std::unique_ptr<DspId> p;
+    void copy(const DspId *o) {
+        if (const bool valid = o && !o->IsNull(); p && valid) {
+            // deep copy onto the already-allocated DspId
+            *p = *o;
+         } else {
+            // allocate a new unique_ptr if `o` is `valid`, otherwise just use nullptr
+            p = valid ? std::make_unique<DspId>(*o) : nullptr;
+        }
+    }
+public:
+    constexpr DspIdPtr() noexcept = default;
+    //! Support conversion construction.
+    //! Note that if dspId.IsNull() then this instance .get() will be nullptr
+    DspIdPtr(const DspId &dspId) { copy(&dspId); }
+    //! Support copy-construction (unlike unique_ptr which does not)
+    DspIdPtr(const DspIdPtr &o) { copy(o.p.get()); }
+    DspIdPtr(DspIdPtr &&o) noexcept : p(std::move(o.p)) {}
+    //! Support copy-assignment (unlike unique_ptr which does not)
+    DspIdPtr &operator=(const DspIdPtr &o) {
+        copy(o.p.get());
+        return *this;
+    }
+    DspIdPtr &operator=(DspIdPtr &&o) noexcept { p = std::move(o.p); return *this; }
+    //! Convenience: Support copy-assignemnt from the underling type directly
+    DspIdPtr &operator=(const DspId &d) {
+        copy(&d);
+        return *this;
+    }
+
+    // -- comparison operators --
+    //! Convenience: Compare for equality directly to a DspId
+    bool operator==(const DspId &d) const {
+        if (p) {
+            return *p == d;
+        } else {
+            return d.IsNull();
+        }
+    }
+    bool operator!=(const DspId &d) const { return !((*this) == d); }
+    bool operator<(const DspId &d) const {
+        if (p) {
+            return *p < d;
+        } else {
+            return DspId{} < d;
+        }
+    }
+    bool operator<=(const DspId &d) const { return (*this) < d || (*this) == d; }
+    bool operator>(const DspId &d) const { return !((*this) <= d); }
+    bool operator>=(const DspId &d) const { return !((*this) < d); }
+
+    // Note: unlike unique_ptr operator<=> comparisons, the below compare the underlying DspId (deep comparison)
+    bool operator==(const DspIdPtr &o) const { return *this == (o.p ? *o.p : DspId{});}
+    bool operator!=(const DspIdPtr &o) const { return *this != (o.p ? *o.p : DspId{});}
+    bool operator<(const DspIdPtr &o) const { return *this < (o.p ? *o.p : DspId{});}
+    bool operator<=(const DspIdPtr &o) const { return *this <= (o.p ? *o.p : DspId{});}
+    bool operator>(const DspIdPtr &o) const { return *this > (o.p ? *o.p : DspId{});}
+    bool operator>=(const DspIdPtr &o) const { return *this >= (o.p ? *o.p : DspId{});}
+
+    // -- unique_ptr work-alike methods --
+    explicit operator bool() const noexcept { return bool(p); }
+    DspId & operator*() { return *p; }
+    const DspId & operator*() const { return *p; }
+    DspId * operator->() { return p.get(); }
+    const DspId * operator->() const { return p.get(); }
+    DspId * get() { return p.get(); }
+    const DspId * get() const { return p.get(); }
+    void reset() { p.reset(); }
+
+    // used by tests
+    std::size_t memUsage() const { return sizeof(*this) + (p ? sizeof(*p) : 0); }
+};
+
+
+#endif // BITCOIN_DSPROOF_DSPID_H
```

### src/dsproof/dsproof.cpp
```diff
@@ -0,0 +1,47 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <dsproof/dsproof.h>
+#include <hash.h>
+
+#include <limits>
+#include <stdexcept>
+
+/* static */
+bool DoubleSpendProof::s_enabled = true;
+
+DoubleSpendProof::DoubleSpendProof()
+{
+}
+
+bool DoubleSpendProof::isEmpty() const
+{
+    // NB: default constructed COutPout has GetN() == 0xffffffff, GetTxId().IsNull().
+    return prevOutIndex() > static_cast<uint32_t>(std::numeric_limits<int32_t>::max())
+            || prevTxId().IsNull() || GetId().IsNull();
+}
+
+void DoubleSpendProof::setHash()
+{
+    m_hash = SerializeHash(*this);
+}
+
+void DoubleSpendProof::checkSanityOrThrow() const
+{
+    if (isEmpty())
+        throw std::runtime_error("DSProof is empty");
+
+    // Check limits for both pushData vectors above
+    for (auto *pushData : {&m_spender1.pushData, &m_spender2.pushData}) {
+        // Message must contain exactly 1 pushData
+        if (pushData->size() != 1)
+            throw std::runtime_error("DSProof must contain exactly 1 pushData");
+        // Script data must be within size limits (520 bytes)
+        if (!pushData->empty() && pushData->front().size() > MaxPushDataSize)
+            throw std::runtime_error("DSProof script size limit exceeded");
+    }
+    if (m_spender1 == m_spender2)
+        throw std::runtime_error("DSProof both spenders are the same");
+}
```

### src/dsproof/dsproof.h
```diff
@@ -0,0 +1,141 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020-2021 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+#ifndef BITCOIN_DSPROOF_DSPROOF_H
+#define BITCOIN_DSPROOF_DSPROOF_H
+
+#include <chain.h> // for cs_main
+#include <dsproof/dspid.h>
+#include <primitives/transaction.h>
+#include <primitives/txid.h>
+#include <script/script.h>
+#include <serialize.h>
+#include <sync.h> // for thread safety macros
+
+class CTxMemPool;
+
+class DoubleSpendProof
+{
+public:
+    //! Limit for the size of a `pushData` vector below
+    static constexpr size_t MaxPushDataSize = MAX_SCRIPT_ELEMENT_SIZE;
+
+    //! Creates an empty DoubleSpendProof
+    DoubleSpendProof();
+
+    //! Creates a DoubleSpendProof for tx1 and tx2 for the given prevout.
+    //!
+    //! Note that this will throw if tx1 or tx2 are invalid, contain invalid
+    //! signatures, don't spend prevout, etc.
+    //!
+    //! Argument `txOut` is the actual previous outpoint's data (used for
+    //! signature verification).  Specify nullptr here to disable signature
+    //! verification (for unit tests).  If this argument is nullptr, the
+    //! generated proof is not guaranteed valid since signatures aren't checked.
+    //!
+    //! Exceptions:
+    //!     std::runtime_error if creation failed
+    //!     std::invalid_argument if tx1.GetHash() == tx2.GetHash()
+    //! (implemented in dsproof_create.cpp)
+    static DoubleSpendProof create(const CTransaction &tx1, const CTransaction &tx2,
+                                   const COutPoint &prevout, const CTxOut *txOut = nullptr);
+
+    bool isEmpty() const;
+
+    enum Validity {
+        Valid,
+        MissingTransaction,
+        MissingUTXO,
+        Invalid
+    };
+
+    const DspId & GetId() const { return m_hash; }
+
+    //! This *must* be called with cs_main and mempool.cs already held!
+    //!
+    //! Optionally, pass the spending tx for this proof, as an optimization; if
+    //! no spendingTx is specified, it will be looked-up in the mempool.
+    //!
+    //! Exceptions: None
+    //! (implemented in dsproof_validate.cpp)
+    Validity validate(const CTxMemPool &mempool, CTransactionRef spendingTx = {}) const EXCLUSIVE_LOCKS_REQUIRED(cs_main);
+
+    const TxId & prevTxId() const { return m_outPoint.GetTxId(); }
+    uint32_t prevOutIndex() const { return m_outPoint.GetN(); }
+    const COutPoint & outPoint() const { return m_outPoint; }
+
+    struct Spender {
+        uint32_t txVersion = 0, outSequence = 0, lockTime = 0;
+        uint256 hashPrevOutputs, hashSequence, hashOutputs;
+        std::vector<std::vector<uint8_t>> pushData;
+        bool operator==(const Spender &o) const {
+            return txVersion == o.txVersion && outSequence == o.outSequence && lockTime == o.lockTime
+                    && hashPrevOutputs == o.hashPrevOutputs && hashSequence == o.hashSequence && hashOutputs == o.hashOutputs
+                    && pushData == o.pushData;
+        }
+        bool operator!=(const Spender &o) const { return !(*this == o); }
+    };
+
+    const Spender & spender1() const { return m_spender1; }
+    const Spender & spender2() const { return m_spender2; }
+
+    // old fashioned serialization.
+    ADD_SERIALIZE_METHODS
+    template <typename Stream, typename Operation>
+    inline void SerializationOp(Stream& s, Operation ser_action) {
+        READWRITE(m_outPoint);
+
+        READWRITE(m_spender1.txVersion);
+        READWRITE(m_spender1.outSequence);
+        READWRITE(m_spender1.lockTime);
+        READWRITE(m_spender1.hashPrevOutputs);
+        READWRITE(m_spender1.hashSequence);
+        READWRITE(m_spender1.hashOutputs);
+        READWRITE(m_spender1.pushData);
+
+        READWRITE(m_spender2.txVersion);
+        READWRITE(m_spender2.outSequence);
+        READWRITE(m_spender2.lockTime);
+        READWRITE(m_spender2.hashPrevOutputs);
+        READWRITE(m_spender2.hashSequence);
+        READWRITE(m_spender2.hashOutputs);
+        READWRITE(m_spender2.pushData);
+
+        // Calculate and save hash (only necessary to do if we are deserializing)
+        if (ser_action.ForRead())
+            setHash();
+    }
+
+
+    // -- Global enable/disable of the double spend proof subsystem.
+
+    //! Returns true if this subsystem is enabled, false otherwise. The double spend proof subsystem can be disabled at
+    //! startup by passing -doublespendproof=0 to bitcoind. Default is enabled.
+    static bool IsEnabled() { return s_enabled; }
+
+    //! Enable/disable the dsproof subsystem. Called by init.cpp at startup. Default is enabled. Note that this
+    //! function is not thread-safe and should only be called once before threads are started to disable.
+    static void SetEnabled(bool b) { s_enabled = b; }
+
+private:
+    COutPoint m_outPoint;           //! Serializable
+    Spender m_spender1, m_spender2; //! Serializable
+
+    DspId m_hash;                   //! In-memory only
+
+    //! Recompute m_hash from serializable data members
+    void setHash();
+
+    /// Throws std::runtime_error if the proof breaks the sanity of:
+    /// - isEmpty()
+    /// - does not have exactly 1 pushData per spender vector
+    /// - any pushData size >520 bytes
+    /// Called from: `create()` and `validate()` (`validate()` won't throw but will return Invalid)
+    void checkSanityOrThrow() const;
+
+    //! Used by IsEnabled() and SetEnabled() static methods; default is: enabled (true)
+    static bool s_enabled;
+};
+
+#endif // BITCOIN_DSPROOF_DSPROOF_H
```

### src/dsproof/dsproof_create.cpp
```diff
@@ -0,0 +1,166 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <dsproof/dsproof.h>
+#include <hash.h>
+#include <script/interpreter.h>
+#include <script/script.h>
+#include <script/sign.h>
+#include <script/standard.h>
+
+#include <stdexcept>
+
+namespace {
+// Non-verifyng signature getter. Used for tests.
+std::vector<uint8_t> getP2PKHSignature(const CScript &script)
+{
+    std::vector<uint8_t> vchRet;
+    auto scriptIter = script.begin();
+    opcodetype type;
+    script.GetOp(scriptIter, type, vchRet);
+
+    if (vchRet.empty())
+        throw std::runtime_error("scriptSig has no signature");
+    const auto hashType = vchRet.back();
+    if (!(hashType & SIGHASH_FORKID))
+        throw std::runtime_error("Tx is not a Bitcoin Cash P2PKH transaction");
+    return vchRet;
+}
+
+// Verifying signature getter. Used for production.
+std::vector<uint8_t> getP2PKHSignature(const CTransaction &tx, unsigned int inputIndex, const CTxOut &txOut)
+{
+    std::vector<uint8_t> vchRet;
+
+    txnouttype outtype;
+    std::vector<CTxDestination> dests;
+    int nReq;
+    if (!ExtractDestinations(txOut.scriptPubKey, outtype, dests, nReq)
+            || nReq != 1 || dests.size() != 1 || outtype != TX_PUBKEYHASH)
+        throw std::runtime_error("TxOut destination is not P2PKH");
+
+    const SignatureData sigData = DataFromTransaction(CMutableTransaction{tx}, inputIndex, txOut);
+    if (!sigData.complete)
+        throw std::runtime_error("Specified tx input is not properly signed");
+    if (sigData.signatures.size() != 1)
+        throw std::runtime_error("Not a P2PKH signature");
+    vchRet = sigData.signatures.begin()->second.second;
+    if (vchRet.empty())
+        throw std::runtime_error("scriptSig has no signature");
+    const auto hashType = vchRet.back();
+    if (!(hashType & SIGHASH_FORKID))
+        throw std::runtime_error("Tx is not a Bitcoin Cash P2PKH transaction");
+
+    return vchRet;
+}
+
+void hashTx(DoubleSpendProof::Spender &spender, const CTransaction &tx, size_t inputIndex)
+{
+    assert(!spender.pushData.empty());
+    assert(!spender.pushData.front().empty());
+    auto hashType = spender.pushData.front().back();
+    if (!(hashType & SIGHASH_ANYONECANPAY)) {
+        CHashWriter ss(SER_GETHASH, 0);
+        for (size_t n = 0; n < tx.vin.size(); ++n) {
+            ss << tx.vin[n].prevout;
+        }
+        spender.hashPrevOutputs = ss.GetHash();
+    }
+    if (!(hashType & SIGHASH_ANYONECANPAY) && (hashType & 0x1f) != SIGHASH_SINGLE
+            && (hashType & 0x1f) != SIGHASH_NONE) {
+        CHashWriter ss(SER_GETHASH, 0);
+        for (size_t n = 0; n < tx.vin.size(); ++n) {
+            ss << tx.vin[n].nSequence;
+        }
+        spender.hashSequence = ss.GetHash();
+    }
+    if ((hashType & 0x1f) != SIGHASH_SINGLE && (hashType & 0x1f) != SIGHASH_NONE) {
+        CHashWriter ss(SER_GETHASH, 0);
+        for (size_t n = 0; n < tx.vout.size(); ++n) {
+            ss << tx.vout[n];
+        }
+        spender.hashOutputs = ss.GetHash();
+    } else if ((hashType & 0x1f) == SIGHASH_SINGLE && inputIndex < tx.vout.size()) {
+        CHashWriter ss(SER_GETHASH, 0);
+        ss << tx.vout[inputIndex];
+        spender.hashOutputs = ss.GetHash();
+    }
+}
+} // namespace
+
+// static
+DoubleSpendProof DoubleSpendProof::create(const CTransaction &tx1, const CTransaction &tx2,
+                                          const COutPoint &prevout, const CTxOut *txOut)
+{
+    DoubleSpendProof answer;
+    if (tx1.GetHash() == tx2.GetHash())
+        throw std::invalid_argument(strprintf("DSProof %s: CTransaction arguments must point to different transactions", __func__));
+    Spender &s1 = answer.m_spender1;
+    Spender &s2 = answer.m_spender2;
+
+    size_t inputIndex1 = 0;
+    size_t inputIndex2 = 0;
+    int foundCt = 0;
+
+    for (; foundCt == 0 && inputIndex1 < tx1.vin.size(); ++inputIndex1) {
+        if (tx1.vin[inputIndex1].prevout == prevout) {
+            ++foundCt;
+            break;
+        }
+    }
+    for (; foundCt == 1 && inputIndex2 < tx2.vin.size(); ++inputIndex2) {
+        if (tx2.vin[inputIndex2].prevout == prevout) {
+            ++foundCt;
+            break;
+        }
+    }
+    if (foundCt != 2)
+        throw std::runtime_error("Transactions do not double spend each other with the specified COutPoint");
+    const CTxIn &in1 = tx1.vin[inputIndex1];
+    const CTxIn &in2 = tx2.vin[inputIndex2];
+    assert(in1.prevout == in2.prevout && in1.prevout == prevout);
+
+    answer.m_outPoint = in1.prevout;
+
+    s1.outSequence = in1.nSequence;
+    s2.outSequence = in2.nSequence;
+
+    // Allow only p2pkh for now.  Below calls to getP2PKHSignature may throw
+    s1.pushData.clear();
+    // may throw
+    s1.pushData.emplace_back( txOut
+                              ? getP2PKHSignature(tx1, inputIndex1, *txOut) // verify sig
+                              : getP2PKHSignature(in1.scriptSig) );         // non-verifying (for test code)
+    s2.pushData.clear();
+    // may throw
+    s2.pushData.emplace_back( txOut
+                              ? getP2PKHSignature(tx2, inputIndex2, *txOut) // verify sig
+                              : getP2PKHSignature(in2.scriptSig) );         // non-verifying (for test code)
+
+    assert(!s1.pushData.front().empty() && !s2.pushData.front().empty());
+
+    s1.txVersion = tx1.nVersion;
+    s2.txVersion = tx2.nVersion;
+    s1.lockTime = tx1.nLockTime;
+    s2.lockTime = tx2.nLockTime;
+
+    hashTx(s1, tx1, inputIndex1);
+    hashTx(s2, tx2, inputIndex2);
+
+    // Sort the spenders so the proof stays the same, independent of the order of tx seen first
+    int32_t diff = s1.hashOutputs.Compare(s2.hashOutputs);
+    if (diff == 0)
+        diff = s1.hashPrevOutputs.Compare(s2.hashPrevOutputs);
+    if (diff > 0)
+        std::swap(s1, s2);
+
+    answer.setHash(); // finally, set the hash
+
+    // Finally, ensure that we can eat our own dog food -- this should always succeed,
+    // it is a programming error if it does not.
+    answer.checkSanityOrThrow();
+
+    return answer;
+}
```

### src/dsproof/dsproof_validate.cpp
```diff
@@ -0,0 +1,161 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <coins.h>
+#include <dsproof/dsproof.h>
+#include <logging.h>
+#include <script/interpreter.h>
+#include <script/script.h>
+#include <script/standard.h>
+#include <txmempool.h>
+#include <validation.h> // for pcoinsTip
+
+#include <stdexcept>
+#include <vector>
+
+namespace {
+class DSPSignatureChecker : public BaseSignatureChecker {
+public:
+    DSPSignatureChecker(const DoubleSpendProof *proof, const DoubleSpendProof::Spender &spender, Amount amount)
+        : m_proof(proof),
+          m_spender(spender),
+          m_amount(amount)
+    {
+    }
+
+    bool CheckSig(const std::vector<uint8_t> &vchSigIn, const std::vector<uint8_t> &vchPubKey, const CScript &scriptCode, uint32_t /*flags*/) const override {
+        CPubKey pubkey(vchPubKey);
+        if (!pubkey.IsValid())
+            return false;
+
+        std::vector<uint8_t> vchSig(vchSigIn);
+        if (vchSig.empty())
+            return false;
+        vchSig.pop_back(); // drop the hashtype byte tacked on to the end of the signature
+
+        CHashWriter ss(SER_GETHASH, 0);
+        ss << m_spender.txVersion << m_spender.hashPrevOutputs << m_spender.hashSequence;
+        ss << m_proof->outPoint();
+        ss << static_cast<const CScriptBase &>(scriptCode);
+        ss << m_amount << m_spender.outSequence << m_spender.hashOutputs;
+        ss << m_spender.lockTime << (int32_t) m_spender.pushData.front().back();
+        const uint256 sighash = ss.GetHash();
+
+        if (vchSig.size() == 64)
+            return pubkey.VerifySchnorr(sighash, vchSig);
+        return pubkey.VerifyECDSA(sighash, vchSig);
+    }
+    bool CheckLockTime(const CScriptNum&) const override {
+        return true;
+    }
+    bool CheckSequence(const CScriptNum&) const override {
+        return true;
+    }
+
+    const DoubleSpendProof *m_proof;
+    const DoubleSpendProof::Spender &m_spender;
+    const Amount m_amount;
+};
+} // namespace
+
+auto DoubleSpendProof::validate(const CTxMemPool &mempool, CTransactionRef spendingTx) const -> Validity
+{
+    AssertLockHeld(cs_main);
+    AssertLockHeld(mempool.cs);
+
+    try {
+        // This ensures not empty and that all pushData vectors have exactly 1 item, among other things.
+        checkSanityOrThrow();
+    } catch (const std::runtime_error &e) {
+        LogPrint(BCLog::DSPROOF, "DoubleSpendProof::%s: %s\n", __func__, e.what());
+        return Invalid;
+    }
+
+    // Check if ordering is proper
+    int32_t diff = m_spender1.hashOutputs.Compare(m_spender2.hashOutputs);
+    if (diff == 0)
+        diff = m_spender1.hashPrevOutputs.Compare(m_spender2.hashPrevOutputs);
+    if (diff > 0)
+        return Invalid; // non-canonical order
+
+    // Get the previous output we are spending.
+    Coin coin;
+    {
+        const CCoinsViewMemPool view(pcoinsTip.get(), mempool); // this checks both mempool coins and confirmed coins
+        if (!view.GetCoin(outPoint(), coin)) {
+            /* if the output we spend is missing then either the tx just got mined
+             * or, more likely, our mempool just doesn't have it.
+             */
+            return MissingUTXO;
+        }
+    }
+    const Amount &amount = coin.GetTxOut().nValue;
+    const CScript &prevOutScript = coin.GetTxOut().scriptPubKey;
+
+    /*
+     * Find the matching transaction spending this. Possibly identical to one
+     * of the sides of this DSP.
+     * We need this because we want the public key that it contains.
+     */
+    if (!spendingTx) {
+        auto it = mempool.mapNextTx.find(m_outPoint);
+        if (it == mempool.mapNextTx.end())
+            return MissingTransaction;
+
+        spendingTx = mempool.get(it->second->GetId());
+    }
+    assert(bool(spendingTx));
+
+    /*
+     * TomZ: At this point (2019-07) we only support P2PKH payments.
+     *
+     * Since we have an actually spending tx, we could trivially support various other
+     * types of scripts because all we need to do is replace the signature from our 'tx'
+     * with the one that comes from the DSP.
+     */
+    const txnouttype scriptType = TX_PUBKEYHASH; // FUTURE: look at prevTx to find out script-type
+
+    std::vector<uint8_t> pubkey;
+    for (const auto &vin : spendingTx->vin) {
+        if (vin.prevout == m_outPoint) {
+            // Found the input script we need!
+            const CScript &inScript = vin.scriptSig;
+            auto scriptIter = inScript.begin();
+            opcodetype type;
+            inScript.GetOp(scriptIter, type); // P2PKH: first signature
+            inScript.GetOp(scriptIter, type, pubkey); // then pubkey
+            break;
+        }
+    }
+
+    if (pubkey.empty())
+        return Invalid;
+
+    CScript inScript;
+    if (scriptType == TX_PUBKEYHASH) {
+        inScript << m_spender1.pushData.front();
+        inScript << pubkey;
+    }
+    DSPSignatureChecker checker1(this, m_spender1, amount);
+    ScriptError error;
+    ScriptExecutionMetrics metrics; // dummy
+
+    if (!VerifyScript(inScript, prevOutScript, 0 /*flags*/, checker1, metrics, &error)) {
+        LogPrint(BCLog::DSPROOF, "DoubleSpendProof failed validating first tx due to %s\n", ScriptErrorString(error));
+        return Invalid;
+    }
+
+    inScript.clear();
+    if (scriptType == TX_PUBKEYHASH) {
+        inScript << m_spender2.pushData.front();
+        inScript << pubkey;
+    }
+    DSPSignatureChecker checker2(this, m_spender2, amount);
+    if (!VerifyScript(inScript, prevOutScript, 0 /*flags*/, checker2, metrics, &error)) {
+        LogPrint(BCLog::DSPROOF, "DoubleSpendProof failed validating second tx due to %s\n", ScriptErrorString(error));
+        return Invalid;
+    }
+    return Valid;
+}
```

### src/dsproof/storage.cpp
```diff
@@ -0,0 +1,238 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <crypto/siphash.h>
+#include <dsproof/storage.h>
+#include <logging.h>
+#include <primitives/transaction.h>
+#include <random.h>
+#include <util/time.h>
+
+#include <cstdint>
+#include <limits>
+#include <stdexcept>
+
+
+DoubleSpendProofStorage::DoubleSpendProofStorage()
+    : m_recentRejects(120000, 0.000001)
+{
+}
+
+//! Helper struct to catch index modify failures (indicates programming error)
+struct DoubleSpendProofStorage::ModFastFail {
+    void operator()(Entry &e) const {
+        LogPrintf("DSProof: Failed to modify m_proofs for entry: %s\n", e.proof.GetId().ToString());
+        assert(!"Internal Error: Failed to modify an m_proofs entry");
+    }
+};
+
+bool DoubleSpendProofStorage::add(const DoubleSpendProof &proof)
+{
+    if (proof.isEmpty()) {
+        // this should never happen and indicates a programming error
+        throw std::invalid_argument(strprintf("%s: DSProof is empty", __func__));
+    }
+
+    LOCK(m_lock);
+
+    const auto &hash = proof.GetId();
+    {
+        auto it = m_proofs.find(hash);
+        if (it != m_proofs.end()) {
+            if (it->orphan) {
+                // mark it as not an orphan now due to explicit add
+                decrementOrphans(1);
+                m_proofs.modify(it, [](Entry &e) { e.orphan = false; }, ModFastFail());
+            }
+            return false;
+        }
+    }
+
+    Entry e;
+    e.proof = proof;
+    m_proofs.emplace(std::move(e));
+    return true;
+}
+
+void DoubleSpendProofStorage::addOrphan(const DoubleSpendProof &proof, NodeId nodeId)
+{
+    LOCK(m_lock);
+    add(proof);
+    const DspId &hash = proof.GetId();
+    auto it = m_proofs.find(hash);
+    assert(it != m_proofs.end()); // cannot happen since above add() call guarantees it now exists
+
+    m_proofs.modify(it, [nodeId, this, &hash](Entry &e) EXCLUSIVE_LOCKS_REQUIRED(m_lock) {
+        if (e.nodeId < 0 && nodeId > -1)
+            e.nodeId = nodeId;
+        if (e.timeStamp < 0)
+            e.timeStamp = GetTime();
+        incrementOrphans(!e.orphan, hash); // actually increments only if orphan false -- may reap older orphans as a side-effect
+        e.orphan = true; // called after to ensure this one makes it in as an orphan even if above reaper reaped
+    }, ModFastFail());
+}
+
+std::list<std::pair<DspId, NodeId>> DoubleSpendProofStorage::findOrphans(const COutPoint &prevOut) const
+{
+    std::list<std::pair<DspId, NodeId>> answer;
+    LOCK(m_lock);
+    const auto iters = m_proofs.get<tag_COutPoint>().equal_range(prevOut);
+    for (auto it = iters.first; it != iters.second; ++it) {
+        if (it->orphan)
+            answer.emplace_back(it->proof.GetId(), it->nodeId);
+    }
+    return answer;
+}
+
+void DoubleSpendProofStorage::claimOrphan(const DspId &hash)
+{
+    LOCK(m_lock);
+    auto it = m_proofs.find(hash);
+    if (it != m_proofs.end() && it->orphan) {
+        decrementOrphans(1);
+        m_proofs.modify(it, [](Entry &e){ e.orphan = false; }, ModFastFail());
+    }
+}
+
+bool DoubleSpendProofStorage::remove(const DspId &hash)
+{
+    LOCK(m_lock);
+    auto it = m_proofs.find(hash);
+    if (it != m_proofs.end()) {
+        decrementOrphans(it->orphan); // actually decrements only if orphan == true
+        m_proofs.erase(it);
+        return true;
+    }
+    return false;
+}
+
+DoubleSpendProof DoubleSpendProofStorage::lookup(const DspId &hash) const
+{
+    DoubleSpendProof ret;
+    LOCK(m_lock);
+    auto it = m_proofs.find(hash);
+    if (it != m_proofs.end())
+        ret = it->proof;
+    return ret;
+}
+
+bool DoubleSpendProofStorage::exists(const DspId &hash) const
+{
+    LOCK(m_lock);
+    return m_proofs.find(hash) != m_proofs.end();
+}
+
+bool DoubleSpendProofStorage::isRecentlyRejectedProof(const DspId &hash) const
+{
+    LOCK(m_lock);
+    return m_recentRejects.contains(hash);
+}
+
+void DoubleSpendProofStorage::markProofRejected(const DspId &hash)
+{
+    LOCK(m_lock);
+    m_recentRejects.insert(hash);
+}
+
+void DoubleSpendProofStorage::newBlockFound()
+{
+    LOCK(m_lock);
+    m_recentRejects.reset();
+}
+
+size_t DoubleSpendProofStorage::size() const {
+    LOCK(m_lock);
+    return m_proofs.size();
+}
+
+void DoubleSpendProofStorage::clear() {
+    LOCK(m_lock);
+    m_proofs.clear();
+    m_recentRejects.reset();
+    m_numOrphans = 0;
+}
+
+DoubleSpendProofStorage::SaltedHasher::SaltedHasher()
+    : k0(GetRand(std::numeric_limits<uint64_t>::max())),
+      k1(GetRand(std::numeric_limits<uint64_t>::max()))
+{}
+
+size_t DoubleSpendProofStorage::SaltedHasher::operator()(const uint256 &hash) const
+{
+    return SipHashUint256(k0, k1, hash);
+}
+
+size_t DoubleSpendProofStorage::SaltedHasher::operator()(const COutPoint &outPoint) const
+{
+    return SipHashUint256Extra(k0, k1, outPoint.GetTxId(), outPoint.GetN());
+}
+
+
+// --- Orphan upkeep (see also storage_cleanup.cpp)
+
+int DoubleSpendProofStorage::secondsToKeepOrphans() const {
+    LOCK(m_lock);
+    return m_secondsToKeepOrphans;
+}
+
+void DoubleSpendProofStorage::setSecondsToKeepOrphans(int secs) {
+    if (secs >= 0) {
+        LOCK(m_lock);
+        m_secondsToKeepOrphans = secs;
+    }
+}
+
+size_t DoubleSpendProofStorage::maxOrphans() const {
+    LOCK(m_lock);
+    return m_maxOrphans;
+}
+void DoubleSpendProofStorage::setMaxOrphans(size_t max) {
+    LOCK(m_lock);
+    m_maxOrphans = max;
+}
+
+size_t DoubleSpendProofStorage::numOrphans() const {
+    LOCK(m_lock);
+    return m_numOrphans;
+}
+
+void DoubleSpendProofStorage::decrementOrphans(size_t n)
+{
+    if (n) {
+        if (m_numOrphans < n)
+            throw std::runtime_error(strprintf("Internal error in DSProof %s: Orphan counter not as expected.", __func__));
+        m_numOrphans -= n;
+    }
+}
+
+void DoubleSpendProofStorage::incrementOrphans(size_t n, const DspId &dontDeleteHash)
+{
+    if (n) {
+        m_numOrphans += n;
+        checkOrphanLimit(dontDeleteHash);
+    }
+}
+
+void DoubleSpendProofStorage::checkOrphanLimit(const DspId &dontDeleteHash)
+{
+    // allow up to 25% more than maxOrphans() as a performance tweak, to avoid this being called for every ophan add.
+    const size_t highWaterMark = size_t(m_maxOrphans * 1.25);
+    const size_t lowWaterMark = m_maxOrphans;
+    if (m_numOrphans > highWaterMark) {
+        // remove oldest first
+        size_t ctr = 0;
+        auto &index = m_proofs.get<tag_TimeStamp>(); // ordered by timestamp
+        for (auto it = index.begin(); it != index.end() && m_numOrphans > lowWaterMark; ) {
+            if (it->orphan && dontDeleteHash != it->proof.GetId()) {
+                it = index.erase(it);
+                decrementOrphans(1);
+                ++ctr;
+            } else
+                ++it;
+        }
+        LogPrint(BCLog::DSPROOF, "DSProof %s: reaped %d orphans, orphan count now %d (thresh-low: %d, thresh-high: %d",
+                 __func__, ctr, m_numOrphans, lowWaterMark, highWaterMark);
+    }
+}
```

### src/dsproof/storage.h
```diff
@@ -0,0 +1,154 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020-2021 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+#ifndef BITCOIN_DSPROOF_STORAGE_H
+#define BITCOIN_DSPROOF_STORAGE_H
+
+#include <bloom.h>
+#include <dsproof/dsproof.h>
+#include <net_nodeid.h>
+#include <sync.h>
+
+#include <boost/multi_index/hashed_index.hpp>
+#include <boost/multi_index/member.hpp>
+#include <boost/multi_index/ordered_index.hpp>
+#include <boost/multi_index_container.hpp>
+
+#include <list>
+#include <utility>
+
+class COutPoint;
+
+class DoubleSpendProofStorage
+{
+public:
+    DoubleSpendProofStorage();
+
+    // Note: All public methods below are thread-safe
+
+    // --- Basic Properties
+
+    /// Returns the number of proofs currently stored (both orphan and non-orphan)
+    size_t size() const;
+
+    /// Returns the numnber of proofs currently stored that are marked as orphans
+    /// This value is always <= .size()
+    size_t numOrphans() const;
+
+    // - Orphan expiry - used by the periodic cleaner, if active, to determine when we expire orphans
+    static constexpr int defaultSecondsToKeepOrphans() { return 90; }
+    int secondsToKeepOrphans() const;
+    void setSecondsToKeepOrphans(int secs);
+
+    // - Orphan limit
+    static constexpr size_t defaultMaxOrphans() { return 65535; }
+    size_t maxOrphans() const;
+    void setMaxOrphans(size_t max);
+
+    // --- Main Methods
+
+    /// Adds a proof, returns true if it did not exist and was added,
+    /// false if it was not added because it already existed.
+    ///
+    /// Note that "adding" an existing orphan is supported. The proof
+    /// will get marked as a non-orphan (equivalent to 'claimOrphan()').
+    ///
+    /// May throw std::invalid_argument if the supplied proof is empty
+    /// or has a null hash.
+    bool add(const DoubleSpendProof &proof);
+    /// Remove by proof-id, returns true if proof was found and removed.
+    bool remove(const DspId &hash);
+
+    /// add()s and additionally registers the proof as an orphan.
+    /// Orphans expire after secondsToKeepOrphans() elapses. They may
+    /// be claimed using 'claimOrphan()'.
+    void addOrphan(const DoubleSpendProof &proof, NodeId peerId);
+    /// Returns all (not yet verified) orphans matching prevOut.
+    /// Each item is a pair of a uint256 and the nodeId that send the proof to us.
+    std::list<std::pair<DspId, NodeId>> findOrphans(const COutPoint &prevOut) const;
+
+    /// Flags the proof associated with hash as not an orphan, and thus
+    /// not subject to automatic expiry.
+    void claimOrphan(const DspId &hash);
+
+    /// Lookup a double-spend proof by id.
+    /// The returned value will be .isEmpty() if the id was not found.
+    DoubleSpendProof lookup(const DspId &hash) const;
+    bool exists(const DspId &hash) const;
+
+    // To be installed from a periodic scheduler task. (Returns true)
+    // (implemented in storage_cleanup.cpp)
+    bool periodicCleanup();
+
+    bool isRecentlyRejectedProof(const DspId &hash) const;
+    void markProofRejected(const DspId &hash);
+    void newBlockFound();
+
+    ///! Completely empties this data structure, clearing all oprhans and known proofs
+    void clear();
+
+private:
+    mutable RecursiveMutex m_lock;
+
+    //! A salted hasher for use with the uint256 type in the IndexProofs set below.
+    //! It may also operate on the COutPoint type as well.
+    //! This code is inspired by txmempool.h's SaltedTxidHasher
+    class SaltedHasher {
+        const uint64_t k0, k1; //! Salt
+    public:
+        SaltedHasher();
+        size_t operator()(const uint256 &hash) const;
+        size_t operator()(const COutPoint &outPoint) const;
+    };
+
+    struct Entry {
+        bool orphan = false;
+        DoubleSpendProof proof;
+        NodeId nodeId = -1;     //! If positive, the bannable peer that told use about this proof.
+        int64_t timeStamp = -1;
+
+        struct Id_Getter {
+            using result_type = DspId;
+            const result_type & operator()(const Entry &e) const { return e.proof.GetId(); }
+        };
+        struct COutPoint_Getter {
+            using result_type = COutPoint;
+            const result_type & operator()(const Entry &e) const { return e.proof.outPoint(); }
+        };
+    };
+    struct ModFastFail; //! back(e) predicate for use with index modifier of m_proofs (quits on failure)
+
+    struct tag_COutPoint {}; //! index tag used below
+    struct tag_TimeStamp {}; //! index tag used below
+
+    using IndexedProofs = boost::multi_index_container<
+        Entry, boost::multi_index::indexed_by<
+                    // indexed by dsproof hash
+                    boost::multi_index::hashed_unique<
+                        Entry::Id_Getter, SaltedHasher>,
+                    // also indexd by COutPoint
+                    boost::multi_index::hashed_non_unique<
+                        boost::multi_index::tag<tag_COutPoint>, Entry::COutPoint_Getter, SaltedHasher>,
+                    // also sorted by timeStamp
+                    boost::multi_index::ordered_non_unique<
+                        boost::multi_index::tag<tag_TimeStamp>, boost::multi_index::member<Entry, int64_t, &Entry::timeStamp>>
+        >
+    >;
+
+    IndexedProofs m_proofs GUARDED_BY(m_lock);
+    CRollingBloomFilter m_recentRejects GUARDED_BY(m_lock);
+
+    // Orphan counter and limits
+    int m_secondsToKeepOrphans GUARDED_BY(m_lock) = defaultSecondsToKeepOrphans();
+    size_t m_maxOrphans GUARDED_BY(m_lock) = defaultMaxOrphans();
+    size_t m_numOrphans GUARDED_BY(m_lock) = 0;
+    //! may throw std::runtime_error if number would go below 0
+    void decrementOrphans(size_t n) EXCLUSIVE_LOCKS_REQUIRED(m_lock);
+    //! implicitly calls checkOrphanLimit()
+    void incrementOrphans(size_t n, const DspId &dontDeleteHash) EXCLUSIVE_LOCKS_REQUIRED(m_lock);
+    //! if number of orphans is above threshold, will delete old orphans
+    void checkOrphanLimit(const DspId &dontDeleteHash) EXCLUSIVE_LOCKS_REQUIRED(m_lock);
+};
+
+#endif // BITCOIN_DSPROOF_STORAGE_H
```

### src/dsproof/storage_cleanup.cpp
```diff
@@ -0,0 +1,40 @@
+// Copyright (C) 2019-2020 Tom Zander <tomz@freedommail.ch>
+// Copyright (C) 2020 Calin Culianu <calin.culianu@gmail.com>
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <dsproof/storage.h>
+#include <logging.h>
+#include <net_processing.h>
+
+bool DoubleSpendProofStorage::periodicCleanup()
+{
+    std::vector<NodeId> punishPeers;
+    {
+        LOCK(m_lock);
+        const auto expire = GetTime() - m_secondsToKeepOrphans;
+        auto &index = m_proofs.get<tag_TimeStamp>();
+        const auto end = index.upper_bound(expire);
+        size_t erased = 0;
+        for (auto it = index.begin(); it != end; ) {
+            if (it->orphan) {
+                if (it->nodeId > -1)
+                    punishPeers.push_back(it->nodeId);
+                it = index.erase(it);
+                decrementOrphans(1);
+                ++erased;
+            } else
+                ++it;
+        }
+        if (erased)
+            LogPrint(BCLog::DSPROOF, "DSP orphans erased: %d, DSProof count: %d\n", erased, m_proofs.size());
+    }
+    if (!punishPeers.empty()) {
+        // mark peers as misbehaving here with m_lock not held
+        LOCK(cs_main);
+        for (auto peerId : punishPeers)
+            Misbehaving(peerId, 1, "dsproof-orphan-expired");
+    }
+
+    return true; // repeat
+}
```

### src/init.cpp
```diff
@@ -19,6 +19,8 @@
 #include <compat/sanity.h>
 #include <config.h>
 #include <consensus/validation.h>
+#include <dsproof/dsproof.h>
+#include <dsproof/storage.h>
 #include <extversion.h>
 #include <flatfile.h>
 #include <fs.h>
@@ -1152,6 +1154,12 @@ void SetupServerArgs() {
                            gbtl::DEFAULT_JOB_DATA_EXPIRY_SECS),
                  false, OptionsCategory::RPC);
 
+    // Double Spend Proof
+    gArgs.AddArg("-doublespendproof",
+                 strprintf("Specify whether to enable or disable the double-spend proof subsystem. If enabled, the node"
+                           " will send and receive double-spend proof messages (default: %d).",
+                           DoubleSpendProof::IsEnabled()), false, OptionsCategory::NODE_RELAY);
+
     // Add the hidden options
     gArgs.AddHiddenArgs(hidden_args);
 }
@@ -1973,6 +1981,11 @@ bool AppInitParameterInteraction(Config &config) {
 
     nMaxTipAge = gArgs.GetArg("-maxtipage", DEFAULT_MAX_TIP_AGE);
 
+    // Option to enable/disable the double-spend proof subsystem (default: enabled)
+    if (const bool def = DoubleSpendProof::IsEnabled(), en = gArgs.GetBoolArg("-doublespendproof", def); en != def) {
+        DoubleSpendProof::SetEnabled(en);
+    }
+
     return true;
 }
 
@@ -2169,6 +2182,13 @@ bool AppInitMain(Config &config, RPCServer &rpcServer,
         }
     }
 
+    /// If the double-spend proof subsystem is enabled, enable the periodic dsproof orphan cleaner task.
+    if (DoubleSpendProof::IsEnabled()) {
+        auto *dspStorage = g_mempool.doubleSpendProofStorage();
+        assert(dspStorage != nullptr);
+        scheduler.scheduleEvery(std::bind(&DoubleSpendProofStorage::periodicCleanup, dspStorage), 60 * 1000);
+    }
+
     // Step 5: verify wallet database integrity
     for (const auto &client : node.chain_clients) {
         if (!client->verify(chainparams)) {
```
