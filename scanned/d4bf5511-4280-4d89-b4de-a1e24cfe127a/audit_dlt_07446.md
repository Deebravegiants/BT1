# [?] tests: Fix lock-order-inversion (potential deadlock) in DoS_tests.

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-04-04
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/6662b89b2fd675466398d30df512a821712fb457
Type: security-commit

## Details
tests: Fix lock-order-inversion (potential deadlock) in DoS_tests.

Summary:
```
Reported by TSAN.

Makes `src/test/test_bitcoin --run_test=DoS_tests` pass also when
compiled with TreadSanitizer (`./configure --with-sanitizers=thread`).
```

Backport of core PR12882
https://github.com/bitcoin/bitcoin/pull/12882/files

Test Plan:
  mkdir build && cd build
  ../configure --with-sanitizers=thread
  make
  export TSAN_OPTIONS="suppressions=${PWD}/../test/sanitizer_suppressions/tsan"
  ./src/test/test_bitcoin -t denialofservice_tests

Reviewers: #bitcoin_abc, deadalnix

Reviewed By: #bitcoin_abc, deadalnix

Differential Revision: https://reviews.bitcoinabc.org/D3606

## Patch
### src/net_processing.h
```diff
@@ -94,7 +94,8 @@ class PeerLogicValidation final : public CValidationInterface,
      * @return                      True if there is more work to be done
      */
     bool SendMessages(const Config &config, CNode *pto,
-                      std::atomic<bool> &interrupt) override;
+                      std::atomic<bool> &interrupt) override
+        EXCLUSIVE_LOCKS_REQUIRED(pto->cs_sendProcessing);
 
     void ConsiderEviction(CNode *pto, int64_t time_in_seconds);
     void
```

### src/test/denialofservice_tests.cpp
```diff
@@ -68,28 +68,43 @@ BOOST_AUTO_TEST_CASE(outbound_slow_chain_eviction) {
     dummyNode1.fSuccessfullyConnected = true;
 
     // This test requires that we have a chain with non-zero work.
-    LOCK(cs_main);
-    BOOST_CHECK(chainActive.Tip() != nullptr);
-    BOOST_CHECK(chainActive.Tip()->nChainWork > 0);
+    {
+        LOCK(cs_main);
+        BOOST_CHECK(chainActive.Tip() != nullptr);
+        BOOST_CHECK(chainActive.Tip()->nChainWork > 0);
+    }
 
     // Test starts here
-    LOCK(dummyNode1.cs_sendProcessing);
-    // should result in getheaders
-    peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
-    LOCK(dummyNode1.cs_vSend);
-    BOOST_CHECK(dummyNode1.vSendMsg.size() > 0);
-    dummyNode1.vSendMsg.clear();
+    {
+        LOCK2(cs_main, dummyNode1.cs_sendProcessing);
+        // should result in getheaders
+        peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    }
+    {
+        LOCK2(cs_main, dummyNode1.cs_vSend);
+        BOOST_CHECK(dummyNode1.vSendMsg.size() > 0);
+        dummyNode1.vSendMsg.clear();
+    }
 
     int64_t nStartTime = GetTime();
     // Wait 21 minutes
     SetMockTime(nStartTime + 21 * 60);
-    // should result in getheaders
-    peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
-    BOOST_CHECK(dummyNode1.vSendMsg.size() > 0);
+    {
+        LOCK2(cs_main, dummyNode1.cs_sendProcessing);
+        // should result in getheaders
+        peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    }
+    {
+        LOCK2(cs_main, dummyNode1.cs_vSend);
+        BOOST_CHECK(dummyNode1.vSendMsg.size() > 0);
+    }
     // Wait 3 more minutes
     SetMockTime(nStartTime + 24 * 60);
-    // should result in disconnect
-    peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode1.cs_sendProcessing);
+        // should result in disconnect
+        peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    }
     BOOST_CHECK(dummyNode1.fDisconnect == true);
     SetMockTime(0);
 
@@ -201,8 +216,10 @@ BOOST_AUTO_TEST_CASE(DoS_banning) {
         // Should get banned.
         Misbehaving(dummyNode1.GetId(), 100, "");
     }
-    LOCK(dummyNode1.cs_sendProcessing);
-    peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode1.cs_sendProcessing);
+        peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    }
     BOOST_CHECK(connman->IsBanned(addr1));
     // Different IP, not banned.
     BOOST_CHECK(!connman->IsBanned(ip(0xa0b0c001 | 0x0000ff00)));
@@ -218,8 +235,10 @@ BOOST_AUTO_TEST_CASE(DoS_banning) {
         LOCK(cs_main);
         Misbehaving(dummyNode2.GetId(), 50, "");
     }
-    LOCK(dummyNode2.cs_sendProcessing);
-    peerLogic->SendMessages(config, &dummyNode2, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode2.cs_sendProcessing);
+        peerLogic->SendMessages(config, &dummyNode2, interruptDummy);
+    }
     // 2 not banned yet...
     BOOST_CHECK(!connman->IsBanned(addr2));
     // ... but 1 still should be.
@@ -228,7 +247,10 @@ BOOST_AUTO_TEST_CASE(DoS_banning) {
         LOCK(cs_main);
         Misbehaving(dummyNode2.GetId(), 50, "");
     }
-    peerLogic->SendMessages(config, &dummyNode2, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode2.cs_sendProcessing);
+        peerLogic->SendMessages(config, &dummyNode2, interruptDummy);
+    }
     BOOST_CHECK(connman->IsBanned(addr2));
 
     bool dummy;
@@ -254,8 +276,10 @@ BOOST_AUTO_TEST_CASE(DoS_banscore) {
         LOCK(cs_main);
         Misbehaving(dummyNode1.GetId(), 100, "");
     }
-    LOCK(dummyNode1.cs_sendProcessing);
-    peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode1.cs_sendProcessing);
+        peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    }
     BOOST_CHECK(!connman->IsBanned(addr1));
     {
         LOCK(cs_main);
@@ -267,7 +291,10 @@ BOOST_AUTO_TEST_CASE(DoS_banscore) {
         LOCK(cs_main);
         Misbehaving(dummyNode1.GetId(), 1, "");
     }
-    peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode1.cs_sendProcessing);
+        peerLogic->SendMessages(config, &dummyNode1, interruptDummy);
+    }
     BOOST_CHECK(connman->IsBanned(addr1));
     gArgs.ForceSetArg("-banscore", std::to_string(DEFAULT_BANSCORE_THRESHOLD));
 
@@ -296,8 +323,10 @@ BOOST_AUTO_TEST_CASE(DoS_bantime) {
         LOCK(cs_main);
         Misbehaving(dummyNode.GetId(), 100, "");
     }
-    LOCK(dummyNode.cs_sendProcessing);
-    peerLogic->SendMessages(config, &dummyNode, interruptDummy);
+    {
+        LOCK2(cs_main, dummyNode.cs_sendProcessing);
+        peerLogic->SendMessages(config, &dummyNode, interruptDummy);
+    }
     BOOST_CHECK(connman->IsBanned(addr));
 
     SetMockTime(nStartTime + 60 * 60);
```
