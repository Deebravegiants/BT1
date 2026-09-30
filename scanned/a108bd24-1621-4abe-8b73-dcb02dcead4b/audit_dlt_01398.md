# [?] Merge bitcoin/bitcoin#34028: p2p: Prevent integer overflow in LocalServiceInfo::nScore

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-06-10
Source: https://github.com/bitcoin/bitcoin/commit/53b836cdcedca79b7504c95b1ba9b6ce7c608b02
Type: security-commit

## Details
Merge bitcoin/bitcoin#34028: p2p: Prevent integer overflow in LocalServiceInfo::nScore

2189a6f5f226d5a2905f1939eb7eea9571502b90 p2p: Saturate LocalServiceInfo::nScore updates at INT_MAX (codeabysss)

Pull request description:

  The overflow for signed arithmetic yields undefined behavior.
  This changes prevents undefined behavior in local address scoring by saturating `nScore` updates at `INT_MAX` in both `SeenLocal()` and `AddLocal()` update paths.

  Fixes: #24049.

ACKs for top commit:
  Crypt-iQ:
    ACK 2189a6f5f226d5a2905f1939eb7eea9571502b90 pending CI
  achow101:
    ACK 2189a6f5f226d5a2905f1939eb7eea9571502b90
  sedited:
    ACK 2189a6f5f226d5a2905f1939eb7eea9571502b90

Tree-SHA512: b861e58ec9d6e18b17768f5cbee31ee825717e1a7216c332eb6fcbe63a7ac24e213ba638aea6f03cb710d9c2d8fe736cc626f11011ed66c3938acf6c38b0ef2a

## Patch
### src/net.cpp
```diff
@@ -29,6 +29,7 @@
 #include <random.h>
 #include <scheduler.h>
 #include <util/fs.h>
+#include <util/overflow.h>
 #include <util/sock.h>
 #include <util/strencodings.h>
 #include <util/thread.h>
@@ -296,7 +297,7 @@ bool AddLocal(const CService& addr_, int nScore)
         const auto [it, is_newly_added] = mapLocalHost.emplace(addr, LocalServiceInfo());
         LocalServiceInfo &info = it->second;
         if (is_newly_added || nScore >= info.nScore) {
-            info.nScore = nScore + (is_newly_added ? 0 : 1);
+            info.nScore = SaturatingAdd(nScore, is_newly_added ? 0 : 1);
             info.nPort = addr.GetPort();
         }
     }
@@ -325,7 +326,7 @@ bool SeenLocal(const CService& addr)
     LOCK(g_maplocalhost_mutex);
     const auto it = mapLocalHost.find(addr);
     if (it == mapLocalHost.end()) return false;
-    ++it->second.nScore;
+    it->second.nScore = SaturatingAdd(it->second.nScore, 1);
     return true;
 }
 
```

### src/test/net_tests.cpp
```diff
@@ -802,6 +802,41 @@ BOOST_AUTO_TEST_CASE(LocalAddress_BasicLifecycle)
     BOOST_CHECK(!IsLocal(addr));
 }
 
+BOOST_AUTO_TEST_CASE(LocalAddress_nScore_Overflow)
+{
+    g_reachable_nets.Add(NET_IPV4);
+    const CService addr{UtilBuildAddress(0x002, 0x001, 0x001, 0x001), 1000}; // 2.1.1.1:1000
+
+    const auto get_score = [](const CService& service) -> int {
+        LOCK(g_maplocalhost_mutex);
+        const auto it = mapLocalHost.find(service);
+        return it != mapLocalHost.end() ? it->second.nScore : 0;
+    };
+
+    const int initial_score = 1000;
+    BOOST_REQUIRE(AddLocal(addr, initial_score));
+    BOOST_REQUIRE(IsLocal(addr));
+    BOOST_CHECK_EQUAL(get_score(addr), initial_score);
+
+    // SeenLocal should increment nScore by 1.
+    BOOST_CHECK(SeenLocal(addr));
+    BOOST_CHECK_EQUAL(get_score(addr), initial_score + 1);
+
+    // AddLocal() saturates nScore when updating an existing entry at INT_MAX.
+    BOOST_REQUIRE(AddLocal(addr, std::numeric_limits<int>::max()));
+    BOOST_CHECK_EQUAL(get_score(addr), std::numeric_limits<int>::max());
+
+    BOOST_CHECK(AddLocal(addr, std::numeric_limits<int>::max()));
+    BOOST_CHECK_EQUAL(get_score(addr), std::numeric_limits<int>::max());
+
+    // SeenLocal() also saturates at INT_MAX.
+    BOOST_CHECK(SeenLocal(addr));
+    BOOST_CHECK_EQUAL(get_score(addr), std::numeric_limits<int>::max());
+
+    RemoveLocal(addr);
+    BOOST_CHECK(!IsLocal(addr));
+}
+
 BOOST_AUTO_TEST_CASE(initial_advertise_from_version_message)
 {
     LOCK(NetEventsInterface::g_msgproc_mutex);
```
