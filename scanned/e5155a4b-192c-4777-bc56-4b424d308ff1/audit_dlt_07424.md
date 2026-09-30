# [?] Seeder: Fix two potential crash bugs plus some code nits

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-02-02
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/7ced6725285a702a1350b515fa6f625c4d7a2fcc
Type: security-commit

## Details
Seeder: Fix two potential crash bugs plus some code nits

Co-authored-by: Axel Gembe <derago@gmail.com>

Summary
---

- Backport this buffer overflow fix from core: https://github.com/sipa/bitcoin-seeder/commit/b1cf356ff28db0425a935678471f9a3a2242042f
- Fix a potential crash if attempting to run seeder with a chain that
  has no checkpoints (and thus `mapCheckpoints` is empty).  Not currently
  an issue for any chain we run, but clearly the rest of the code
  intended to support running on a chain with no checkpoints, yet this 1
  place in bitcoin.cpp would crash if on such a chain.
- Nit: Fixed grabbing net magic by copy rather than by reference in
  `ProcessMessages`.
- Nit: Got rid of C macros `BEGIN(`) and `END()` in favor of an explicit
  expression in the 1 place they are used in this code, and made this
  expression safer should someone ever change the sign of `CDataStream`'s
  `value_type`.
- Nit: `static inline` -> simply `inline` for the Sleep function, since
  the latter is more idiomatic for header-only inline functions.
- Nit: Clamp `nMilliSec` in `Sleep()` to >= 0. Sleeping for negative
  time has been shown to be buggy on some older libstdc++
  implementations.
- Nit: added `const`-correctness in a couple of places.

Test Plan
---

- `ninja bitcoin-seeder check-bitcoin-seeder`
- Run the seeder and make sure it still works:
`bitcoin-seeder -host=seed.bch.loping.net -ns=iris.loping.net -mbox=derago.gmail.com -port=5353`

## Patch
### src/seeder/bitcoin.cpp
```diff
@@ -121,11 +121,13 @@ PeerMessagingState CSeederNode::ProcessMessage(const std::string &strCommand,
         if (vAddr) {
             BeginMessage("getaddr");
             EndMessage();
-            std::vector<BlockHash> locatorHash(
-                1, Params().Checkpoints().mapCheckpoints.rbegin()->second);
-            BeginMessage(NetMsgType::GETHEADERS);
-            vSend << CBlockLocator(locatorHash) << uint256();
-            EndMessage();
+            // request headers starting after last checkpoint (only if we have checkpoints for this network)
+            if (const auto &mapCheckpoints = Params().Checkpoints().mapCheckpoints; !mapCheckpoints.empty()) {
+                std::vector<BlockHash> locatorHash(1, mapCheckpoints.rbegin()->second);
+                BeginMessage(NetMsgType::GETHEADERS);
+                vSend << CBlockLocator(locatorHash) << uint256();
+                EndMessage();
+            }
             doneAfter = std::time(nullptr) + GetTimeout();
         } else {
             doneAfter = std::time(nullptr) + 1;
@@ -201,12 +203,14 @@ bool CSeederNode::ProcessMessages() {
         return false;
     }
 
-    const CMessageHeader::MessageMagic netMagic = Params().NetMagic();
+    const CMessageHeader::MessageMagic &netMagic = Params().NetMagic();
 
     do {
-        CDataStream::iterator pstart = std::search(
-            vRecv.begin(), vRecv.end(), BEGIN(netMagic), END(netMagic));
-        std::size_t nHeaderSize =
+        using CharPtrT = const CDataStream::value_type *; // ensure compare of the same sign of char * for std::search
+        const CDataStream::iterator pstart = std::search(
+            vRecv.begin(), vRecv.end(),
+            reinterpret_cast<CharPtrT>(netMagic.data()), reinterpret_cast<CharPtrT>(netMagic.data() + netMagic.size()));
+        const std::size_t nHeaderSize =
             GetSerializeSize(CMessageHeader(netMagic), vRecv.GetVersion());
         if (std::size_t(vRecv.end() - pstart) < nHeaderSize) {
             if (vRecv.size() > nHeaderSize) {
```

### src/seeder/dns.cpp
```diff
@@ -242,7 +242,7 @@ static int write_record_aaaa(uint8_t **outpos, const uint8_t *outend,
     if (ret) {
         return ret;
     }
-    if (outend - *outpos < 6) {
+    if (outend - *outpos < 18) {
         error = -5;
         goto error;
     }
```

### src/seeder/util.h
```diff
@@ -5,14 +5,12 @@
 #ifndef BITCOIN_SEEDER_UTIL_H
 #define BITCOIN_SEEDER_UTIL_H
 
+#include <algorithm>
 #include <chrono>
 #include <thread>
 
-#define BEGIN(a) ((char *)&(a))
-#define END(a) ((char *)&((&(a))[1]))
-
-static inline void Sleep(int nMilliSec) {
-    std::this_thread::sleep_for(std::chrono::milliseconds{nMilliSec});
+inline void Sleep(int nMilliSec) {
+    std::this_thread::sleep_for(std::chrono::milliseconds{std::max(0, nMilliSec)});
 }
 
 #endif // BITCOIN_SEEDER_UTIL_H
```
