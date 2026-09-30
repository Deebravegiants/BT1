# [?] Fix potential deadlock (#5124)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2024-11-06
Source: https://github.com/XRPLF/rippled/commit/9e48fc0c834e8a6e340c521e9ec58b97b944c1fd
Type: security-commit

## Details
Fix potential deadlock (#5124)

* 2.2.2 changed functions acquireAsync and NetworkOPsImp::recvValidation to add an item to a collection under lock, unlock, do some work, then lock again to do remove the item. It will deadlock if an exception is thrown while adding the item - before unlocking.
* Replace ScopedUnlock with scope_unlock.

## Patch
### include/xrpl/basics/scope.h
```diff
@@ -21,6 +21,7 @@
 #define RIPPLE_BASICS_SCOPE_H_INCLUDED
 
 #include <exception>
+#include <mutex>
 #include <type_traits>
 #include <utility>
 
@@ -186,6 +187,70 @@ class scope_success
 template <class EF>
 scope_success(EF) -> scope_success<EF>;
 
+/**
+    Automatically unlocks and re-locks a unique_lock object.
+
+    This is the reverse of a std::unique_lock object - instead of locking the
+   mutex for the lifetime of this object, it unlocks it.
+
+    Make sure you don't try to unlock mutexes that aren't actually locked!
+
+    This is essentially a less-versatile boost::reverse_lock.
+
+    e.g. @code
+
+    std::mutex mut;
+
+    for (;;)
+    {
+        std::unique_lock myScopedLock{mut};
+        // mut is now locked
+
+        ... do some stuff with it locked ..
+
+        while (xyz)
+        {
+            ... do some stuff with it locked ..
+
+            scope_unlock unlocker{myScopedLock};
+
+            // mut is now unlocked for the remainder of this block,
+            // and re-locked at the end.
+
+            ...do some stuff with it unlocked ...
+        }  // mut gets locked here.
+
+    }  // mut gets unlocked here
+    @endcode
+*/
+
+template <class Mutex>
+class scope_unlock
+{
+    std::unique_lock<Mutex>* plock;
+
+public:
+    explicit scope_unlock(std::unique_lock<Mutex>& lock) noexcept(true)
+        : plock(&lock)
+    {
+        assert(plock->owns_lock());
+        plock->unlock();
+    }
+
+    // Immovable type
+    scope_unlock(scope_unlock const&) = delete;
+    scope_unlock&
+    operator=(scope_unlock const&) = delete;
+
+    ~scope_unlock() noexcept(true)
+    {
+        plock->lock();
+    }
+};
+
+template <class Mutex>
+scope_unlock(std::unique_lock<Mutex>&) -> scope_unlock<Mutex>;
+
 }  // namespace ripple
 
 #endif
```

### src/xrpld/app/ledger/detail/InboundLedgers.cpp
```diff
@@ -25,9 +25,11 @@
 #include <xrpld/perflog/PerfLog.h>
 #include <xrpl/basics/DecayingSample.h>
 #include <xrpl/basics/Log.h>
+#include <xrpl/basics/scope.h>
 #include <xrpl/beast/container/aged_map.h>
 #include <xrpl/beast/core/LexicalCast.h>
 #include <xrpl/protocol/jss.h>
+
 #include <exception>
 #include <memory>
 #include <mutex>
@@ -139,7 +141,7 @@ class InboundLedgersImp : public InboundLedgers
             if (pendingAcquires_.contains(hash))
                 return;
             pendingAcquires_.insert(hash);
-            lock.unlock();
+            scope_unlock unlock(lock);
             acquire(hash, seq, reason);
         }
         catch (std::exception const& e)
@@ -154,7 +156,6 @@ class InboundLedgersImp : public InboundLedgers
                 << "Unknown exception thrown for acquiring new inbound ledger "
                 << hash;
         }
-        lock.lock();
         pendingAcquires_.erase(hash);
     }
 
```

### src/xrpld/app/ledger/detail/LedgerMaster.cpp
```diff
@@ -46,10 +46,12 @@
 #include <xrpl/basics/UptimeClock.h>
 #include <xrpl/basics/contract.h>
 #include <xrpl/basics/safe_cast.h>
+#include <xrpl/basics/scope.h>
 #include <xrpl/protocol/BuildInfo.h>
 #include <xrpl/protocol/HashPrefix.h>
 #include <xrpl/protocol/digest.h>
 #include <xrpl/resource/Fees.h>
+
 #include <algorithm>
 #include <cassert>
 #include <chrono>
@@ -60,86 +62,6 @@
 
 namespace ripple {
 
-namespace {
-
-//==============================================================================
-/**
-    Automatically unlocks and re-locks a unique_lock object.
-
-    This is the reverse of a std::unique_lock object - instead of locking the
-   mutex for the lifetime of this object, it unlocks it.
-
-    Make sure you don't try to unlock mutexes that aren't actually locked!
-
-    This is essentially a less-versatile boost::reverse_lock.
-
-    e.g. @code
-
-    std::mutex mut;
-
-    for (;;)
-    {
-        std::unique_lock myScopedLock{mut};
-        // mut is now locked
-
-        ... do some stuff with it locked ..
-
-        while (xyz)
-        {
-            ... do some stuff with it locked ..
-
-            ScopedUnlock unlocker{myScopedLock};
-
-            // mut is now unlocked for the remainder of this block,
-            // and re-locked at the end.
-
-            ...do some stuff with it unlocked ...
-        }  // mut gets locked here.
-
-    }  // mut gets unlocked here
-    @endcode
-*/
-template <class MutexType>
-class ScopedUnlock
-{
-    std::unique_lock<MutexType>& lock_;
-
-public:
-    /** Creates a ScopedUnlock.
-
-        As soon as it is created, this will unlock the unique_lock, and
-        when the ScopedLock object is deleted, the unique_lock will
-        be re-locked.
-
-        Make sure this object is created and deleted by the same thread,
-        otherwise there are no guarantees what will happen! Best just to use it
-        as a local stack object, rather than creating on the heap.
-    */
-    explicit ScopedUnlock(std::unique_lock<MutexType>& lock) : lock_(lock)
-    {
-        assert(lock_.owns_lock());
-        lock_.unlock();
-    }
-
-    ScopedUnlock(ScopedUnlock const&) = delete;
-    ScopedUnlock&
-    operator=(ScopedUnlock const&) = delete;
-
-    /** Destructor.
-
-        The unique_lock will be locked after the destructor is called.
-
-        Make sure this object is created and deleted by the same thread,
-        otherwise there are no guarantees what will happen!
-    */
-    ~ScopedUnlock() noexcept(false)
-    {
-        lock_.lock();
-    }
-};
-
-}  // namespace
-
 // Don't catch up more than 100 ledgers (cannot exceed 256)
 static constexpr int MAX_LEDGER_GAP{100};
 
@@ -1336,7 +1258,7 @@ LedgerMaster::findNewLedgersToPublish(
     auto valLedger = mValidLedger.get();
     std::uint32_t valSeq = valLedger->info().seq;
 
-    ScopedUnlock sul{sl};
+    scope_unlock sul{sl};
     try
     {
         for (std::uint32_t seq = pubSeq; seq <= valSeq; ++seq)
@@ -1882,7 +1804,7 @@ LedgerMaster::fetchForHistory(
     InboundLedger::Reason reason,
     std::unique_lock<std::recursive_mutex>& sl)
 {
-    ScopedUnlock sul{sl};
+    scope_unlock sul{sl};
     if (auto hash = getLedgerHashForHistory(missing, reason))
     {
         assert(hash->isNonZero());
@@ -2052,7 +1974,7 @@ LedgerMaster::doAdvance(std::unique_lock<std::recursive_mutex>& sl)
             for (auto const& ledger : pubLedgers)
             {
                 {
-                    ScopedUnlock sul{sl};
+                    scope_unlock sul{sl};
                     JLOG(m_journal.debug())
                         << "tryAdvance publishing seq " << ledger->info().seq;
                     setFullLedger(ledger, true, true);
@@ -2061,7 +1983,7 @@ LedgerMaster::doAdvance(std::unique_lock<std::recursive_mutex>& sl)
                 setPubLedger(ledger);
 
                 {
-                    ScopedUnlock sul{sl};
+                    scope_unlock sul{sl};
                     app_.getOPs().pubLedger(ledger);
                 }
             }
```

### src/xrpld/app/misc/NetworkOPs.cpp
```diff
@@ -53,6 +53,7 @@
 #include <xrpl/basics/UptimeClock.h>
 #include <xrpl/basics/mulDiv.h>
 #include <xrpl/basics/safe_cast.h>
+#include <xrpl/basics/scope.h>
 #include <xrpl/beast/rfc2616.h>
 #include <xrpl/beast/utility/rngfill.h>
 #include <xrpl/crypto/RFC1751.h>
@@ -2310,7 +2311,7 @@ NetworkOPsImp::recvValidation(
             bypassAccept = BypassAccept::yes;
         else
             pendingValidations_.insert(val->getLedgerHash());
-        lock.unlock();
+        scope_unlock unlock(lock);
         handleNewValidation(app_, val, source, bypassAccept, m_journal);
     }
     catch (std::exception const& e)
@@ -2327,10 +2328,9 @@ NetworkOPsImp::recvValidation(
     }
     if (bypassAccept == BypassAccept::no)
     {
-        lock.lock();
         pendingValidations_.erase(val->getLedgerHash());
-        lock.unlock();
     }
+    lock.unlock();
 
     pubValidation(val);
 
```
