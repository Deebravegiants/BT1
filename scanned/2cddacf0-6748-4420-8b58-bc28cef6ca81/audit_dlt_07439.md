# [?] fix a deserialization overflow edge case

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-11-13
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/ec5df583ca34cab0ead490ea73f14a4302599b02
Type: security-commit

## Details
fix a deserialization overflow edge case

Summary:
```
A specially-constructed BlockTransactionsRequest can cause offset to
wrap in deserialization. In the current code, there is not any way this
could be dangerous; but disallowing it reduces the potential for future
surprises.
```

Backport of core [[https://github.com/bitcoin/bitcoin/pull/14685/files | PR14685]].

The bug this PR is fixing doesn't apply directly to our code, since we
are already using 32 bit indexes (renames indices) since D1146 and the
deserialization size is limited to 0x02000000 by the `MAX_SIZE` constant
(see https://bitcoin.org/en/developer-reference#message-headers), so
`MAX_SIZE < max(uint32_t)` is the limiting factor for us.
In the meantime the overflow issue will occur if the `MAX_SIZE` constant
is raised above `max(uint32_t)`.

This diff is also adapted to test the `BlockTransactionRequest`
deserialization against `MAX_SIZE` and make sure the overflow edge-case
is un der control should the constant get raised. Static asserts will
cause the build to fail if the tests assumptions are no longer valid.

Test Plan:
  ninja all check
  ./test/functional/test_runner.py abc-p2p-compactblocks

Reviewers: #bitcoin_abc, deadalnix, jasonbcox

Reviewed By: #bitcoin_abc, jasonbcox

Subscribers: jasonbcox

Differential Revision: https://reviews.bitcoinabc.org/D5049

## Patch
### src/blockencodings.h
```diff
@@ -56,14 +56,14 @@ class BlockTransactionsRequest {
                 }
             }
 
-            uint32_t offset = 0;
+            uint64_t offset = 0;
             for (auto &index : indices) {
-                if (uint64_t(index) + uint64_t(offset) >
+                if (uint64_t(index) + offset >
                     std::numeric_limits<uint32_t>::max()) {
                     throw std::ios_base::failure("indices overflowed 32 bits");
                 }
                 index = index + offset;
-                offset = index + 1;
+                offset = uint64_t(index) + 1;
             }
         } else {
             for (size_t i = 0; i < indices.size(); i++) {
@@ -206,6 +206,10 @@ class CBlockHeaderAndShortTxIDs {
 
         READWRITE(prefilledtxn);
 
+        if (BlockTxCount() > std::numeric_limits<uint32_t>::max()) {
+            throw std::ios_base::failure("indices overflowed 32 bits");
+        }
+
         if (ser_action.ForRead()) {
             FillShortTxIDSelector();
         }
```

### src/test/blockencodings_tests.cpp
```diff
@@ -64,6 +64,18 @@ static CBlock BuildBlockTestCase() {
     return block;
 }
 
+// BOOST_CHECK_EXCEPTION predicates to check the exception message
+class HasReason {
+public:
+    HasReason(const std::string &reason) : m_reason(reason) {}
+    bool operator()(const std::exception &e) const {
+        return std::string(e.what()).find(m_reason) != std::string::npos;
+    };
+
+private:
+    const std::string m_reason;
+};
+
 // Number of shared use_counts we expect for a tx we haven't touched
 // (block + mempool + our copy from the GetSharedTx call)
 constexpr long SHARED_TX_OFFSET{3};
@@ -413,4 +425,65 @@ BOOST_AUTO_TEST_CASE(TransactionsRequestSerializationTest) {
     BOOST_CHECK_EQUAL(req1.indices[3], req2.indices[3]);
 }
 
+BOOST_AUTO_TEST_CASE(TransactionsRequestDeserializationMaxTest) {
+    // Check that the highest legal index is decoded correctly
+    BlockTransactionsRequest req0;
+    req0.blockhash = BlockHash(InsecureRand256());
+    req0.indices.resize(1);
+
+    using indiceType = decltype(req0.indices)::value_type;
+    static_assert(MAX_SIZE < std::numeric_limits<indiceType>::max(),
+                  "The max payload size cannot fit into the indice type");
+
+    req0.indices[0] = MAX_SIZE;
+
+    CDataStream stream(SER_NETWORK, PROTOCOL_VERSION);
+    stream << req0;
+
+    BlockTransactionsRequest req1;
+    stream >> req1;
+    BOOST_CHECK_EQUAL(req0.indices.size(), req1.indices.size());
+    BOOST_CHECK_EQUAL(req0.indices[0], req1.indices[0]);
+
+    req0.indices[0] += 1;
+    stream << req0;
+    BlockTransactionsRequest req2;
+    BOOST_CHECK_EXCEPTION(stream >> req2, std::ios_base::failure,
+                          HasReason("ReadCompactSize(): size too large"));
+}
+
+BOOST_AUTO_TEST_CASE(TransactionsRequestDeserializationOverflowTest) {
+    // Any set of index deltas that starts with N values that sum to
+    // (0x100000000 - N) causes the edge-case overflow that was originally not
+    // checked for. Such a request cannot be created by serializing a real
+    // BlockTransactionsRequest due to the overflow, so here we'll serialize
+    // from raw deltas. This can only occur if MAX_SIZE is greater than the
+    // maximum value for that the indice type can handle.
+    BlockTransactionsRequest req0;
+    req0.blockhash = BlockHash(InsecureRand256());
+    req0.indices.resize(3);
+
+    using indiceType = decltype(req0.indices)::value_type;
+    static_assert(std::is_same<indiceType, uint32_t>::value,
+                  "This test expects the indice type to be an uint32_t");
+
+    req0.indices[0] = 0x7000;
+    req0.indices[1] = 0x100000000 - 0x7000 - 2;
+    req0.indices[2] = 0;
+    CDataStream stream(SER_NETWORK, PROTOCOL_VERSION);
+    stream << req0.blockhash;
+    WriteCompactSize(stream, req0.indices.size());
+    WriteCompactSize(stream, req0.indices[0]);
+    WriteCompactSize(stream, req0.indices[1]);
+    WriteCompactSize(stream, req0.indices[2]);
+
+    BlockTransactionsRequest req1;
+    // If MAX_SIZE is the limiting factor, the deserialization should throw.
+    // Otherwise make sure that the overflow edge-case is under control.
+    BOOST_CHECK_EXCEPTION(stream >> req1, std::ios_base::failure,
+                          HasReason((MAX_SIZE < req0.indices[1])
+                                        ? "ReadCompactSize(): size too large"
+                                        : "indices overflowed 32 bits"));
+}
+
 BOOST_AUTO_TEST_SUITE_END()
```
