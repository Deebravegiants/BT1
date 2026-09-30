# [?] Fix CCheckQueue IsIdle (potential) race condition and remove dangerous constructors.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2017-01-09
Source: https://github.com/zcash/zcash/commit/8e67b36e865e2ed5e0dce44817636fe6bcb4222c
Type: security-commit

## Details
Fix CCheckQueue IsIdle (potential) race condition and remove dangerous constructors.

zcash: cherry picked from commit e2073424fd5a185781750347fbfbb0c108ef66fd
zcash: https://github.com/bitcoin/bitcoin/pull/9497

## Patch
### src/checkqueue.h
```diff
@@ -12,6 +12,8 @@
 #include <boost/thread/locks.hpp>
 #include <boost/thread/mutex.hpp>
 
+#include "sync.h"
+
 template <typename T>
 class CCheckQueueControl;
 
@@ -126,6 +128,9 @@ class CCheckQueue
     }
 
 public:
+    //! Mutex to ensure only one concurrent CCheckQueueControl
+    boost::mutex ControlMutex;
+
     //! Create a new check queue
     CCheckQueue(unsigned int nBatchSizeIn) : nIdle(0), nTotal(0), fAllOk(true), nTodo(0), fQuit(false), nBatchSize(nBatchSizeIn) {}
 
@@ -160,12 +165,6 @@ class CCheckQueue
     {
     }
 
-    bool IsIdle()
-    {
-        boost::unique_lock<boost::mutex> lock(mutex);
-        return (nTotal == nIdle && nTodo == 0 && fAllOk == true);
-    }
-
 };
 
 /** 
@@ -176,16 +175,18 @@ template <typename T>
 class CCheckQueueControl
 {
 private:
-    CCheckQueue<T>* pqueue;
+    CCheckQueue<T> * const pqueue;
     bool fDone;
 
 public:
-    CCheckQueueControl(CCheckQueue<T>* pqueueIn) : pqueue(pqueueIn), fDone(false)
+    CCheckQueueControl() = delete;
+    CCheckQueueControl(const CCheckQueueControl&) = delete;
+    CCheckQueueControl& operator=(const CCheckQueueControl&) = delete;
+    explicit CCheckQueueControl(CCheckQueue<T> * const pqueueIn) : pqueue(pqueueIn), fDone(false)
     {
         // passed queue is supposed to be unused, or NULL
         if (pqueue != NULL) {
-            bool isIdle = pqueue->IsIdle();
-            assert(isIdle);
+            ENTER_CRITICAL_SECTION(pqueue->ControlMutex);
         }
     }
 
@@ -208,6 +209,9 @@ class CCheckQueueControl
     {
         if (!fDone)
             Wait();
+        if (pqueue != NULL) {
+            LEAVE_CRITICAL_SECTION(pqueue->ControlMutex);
+        }
     }
 };
 
```
