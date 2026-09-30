# [?] Avoid a race condition during peer status change

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2019-02-23
Source: https://github.com/XRPLF/rippled/commit/9dbf8495eed1f8e862fe69869bba56a694e00815
Type: security-commit

## Details
Avoid a race condition during peer status change

## Patch
### src/ripple/overlay/impl/PeerImp.cpp
```diff
@@ -1658,15 +1658,13 @@ PeerImp::onMessage (std::shared_ptr <protocol::TMStatusChange> const& m)
 
     if (m->has_firstseq () && m->has_lastseq())
     {
+        std::lock_guard<std::mutex> sl (recentLock_);
+
         minLedger_ = m->firstseq ();
         maxLedger_ = m->lastseq ();
 
-        // VFALCO Is this workaround still needed?
-        // Work around some servers that report sequences incorrectly
-        if (minLedger_ == 0)
-            maxLedger_ = 0;
-        if (maxLedger_ == 0)
-            minLedger_ = 0;
+        if ((maxLedger_ < minLedger_) || (minLedger_ == 0) || (maxLedger_ == 0))
+            minLedger_ = maxLedger_ = 0;
     }
 
     if (m->has_ledgerseq() &&
```
