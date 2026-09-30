# [?] Fix heap-use-after-free in activation_tests

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2019-12-21
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/31e8c49e22cae666679a97dd1e34e028571301d9
Type: security-commit

## Details
Fix heap-use-after-free in activation_tests

Summary: CreateChainParams() returns a unique_ptr that ends up with no owner. This patch fixes that.

Test Plan:
```
cmake -GNinja -DCMAKE_BUILD_TYPE=Debug -DENABLE_SANITIZERS=address -DCCACHE=OFF ..
ninja test_bitcoin
./src/test/test_bitcoin --run_test=activation_tests
```
Before patch: Same failure as seen here: https://build.bitcoinabc.org/viewLog.html?buildId=24568&buildTypeId=BitcoinABC_Master_BitcoinAbcMasterAsan&tab=buildLog&_focus=1047
After patch: No errors detected

Reviewers: #bitcoin_abc, deadalnix, Fabien

Reviewed By: #bitcoin_abc, deadalnix, Fabien

Subscribers: Fabien

Differential Revision: https://reviews.bitcoinabc.org/D4795

## Patch
### src/test/activation_tests.cpp
```diff
@@ -24,21 +24,21 @@ static void SetMTP(std::array<CBlockIndex, 12> &blocks, int64_t mtp) {
 }
 
 BOOST_AUTO_TEST_CASE(isgravitonenabled) {
-    const auto &params =
-        CreateChainParams(CBaseChainParams::MAIN)->GetConsensus();
+    const auto params = CreateChainParams(CBaseChainParams::MAIN);
+    const auto &consensus = params->GetConsensus();
 
-    BOOST_CHECK(!IsGravitonEnabled(params, nullptr));
+    BOOST_CHECK(!IsGravitonEnabled(consensus, nullptr));
 
     std::array<CBlockIndex, 4> blocks;
-    blocks[0].nHeight = params.gravitonHeight - 2;
+    blocks[0].nHeight = consensus.gravitonHeight - 2;
     for (size_t i = 1; i < blocks.size(); ++i) {
         blocks[i].pprev = &blocks[i - 1];
         blocks[i].nHeight = blocks[i - 1].nHeight + 1;
     }
-    BOOST_CHECK(!IsGravitonEnabled(params, &blocks[0]));
-    BOOST_CHECK(!IsGravitonEnabled(params, &blocks[1]));
-    BOOST_CHECK(IsGravitonEnabled(params, &blocks[2]));
-    BOOST_CHECK(IsGravitonEnabled(params, &blocks[3]));
+    BOOST_CHECK(!IsGravitonEnabled(consensus, &blocks[0]));
+    BOOST_CHECK(!IsGravitonEnabled(consensus, &blocks[1]));
+    BOOST_CHECK(IsGravitonEnabled(consensus, &blocks[2]));
+    BOOST_CHECK(IsGravitonEnabled(consensus, &blocks[3]));
 }
 
 BOOST_AUTO_TEST_CASE(isphononenabled) {
```
